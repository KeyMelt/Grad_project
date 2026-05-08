from __future__ import annotations

import ast
import asyncio
from asyncio.subprocess import Process
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import mkdtemp
from typing import Any, Optional
from uuid import uuid4

from backend.exercise_templates import build_blank_diagnostics
from backend.lessons import get_lesson_definition
from backend.workspace_store_sqlite import SqliteWorkspaceStore


class WorkspaceRuntimeError(Exception):
    def __init__(self, status_code: int, detail: Any):
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail


@dataclass
class WorkspaceRunRecord:
    run_id: str
    status: str
    exit_code: Optional[int] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: Optional[str] = None


@dataclass
class WorkspaceSessionRecord:
    session_id: str
    lesson_id: str
    workspace_dir: Path
    visible_files: list[str]
    file_versions: dict[str, int]
    console_process: Process
    runtime_mode: str
    console_ready: bool = False
    listeners: set[asyncio.Queue[dict[str, Any]]] = field(default_factory=set)
    reader_task: Optional[asyncio.Task[None]] = None
    runs: dict[str, WorkspaceRunRecord] = field(default_factory=dict)
    last_prompt: str = ">>> "


CONSOLE_HELPER_FILENAME = ".workspace_console.py"

CONSOLE_HELPER_SOURCE = r"""
import code
import contextlib
import io
import json
import sys
import traceback

globals_ns = {"__name__": "__main__"}
console = code.InteractiveConsole(globals_ns)


def emit(payload):
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


emit({"type": "ready"})
emit({"type": "prompt", "prompt": ">>> "})
more = False

for raw_line in sys.stdin:
    raw_line = raw_line.strip()
    if not raw_line:
        continue

    try:
        command = json.loads(raw_line)
    except json.JSONDecodeError:
        emit({"type": "stderr", "data": "Invalid console command.\n"})
        emit({"type": "prompt", "prompt": "... " if more else ">>> "})
        continue

    command_type = command.get("type")
    if command_type == "input":
        line = command.get("line", "")
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            try:
                more = console.push(line)
            except Exception:
                more = False
                traceback.print_exc()
        stdout_value = stdout_buffer.getvalue()
        stderr_value = stderr_buffer.getvalue()
        if stdout_value:
            emit({"type": "stdout", "data": stdout_value})
        if stderr_value:
            emit({"type": "stderr", "data": stderr_value})
        emit({"type": "prompt", "prompt": "... " if more else ">>> "})
        continue

    if command_type == "run_script":
        run_id = command.get("run_id", "")
        path = command.get("path", "script.py")
        emit({"type": "run_started", "run_id": run_id})
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        exit_code = 0
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            try:
                source = open(path, "r", encoding="utf-8").read()
                compiled = compile(source, path, "exec")
                exec(compiled, globals_ns)
            except SystemExit as exc:
                if isinstance(exc.code, int):
                    exit_code = exc.code
                else:
                    exit_code = 1 if exc.code else 0
            except Exception:
                exit_code = 1
                traceback.print_exc()
        stdout_value = stdout_buffer.getvalue()
        stderr_value = stderr_buffer.getvalue()
        if stdout_value:
            emit({"type": "stdout", "data": stdout_value, "run_id": run_id})
        if stderr_value:
            emit({"type": "stderr", "data": stderr_value, "run_id": run_id})
        if exit_code == 0:
            emit({"type": "run_finished", "run_id": run_id, "exit_code": exit_code})
        else:
            emit({"type": "run_failed", "run_id": run_id, "exit_code": exit_code})
        emit({"type": "prompt", "prompt": ">>> "})
        continue

    emit({"type": "stderr", "data": f"Unsupported command: {command_type}\n"})
    emit({"type": "prompt", "prompt": "... " if more else ">>> "})
""".strip()


class WorkspaceSessionService:
    def __init__(
        self,
        *,
        base_dir: str | None = None,
        sandbox_image: str = "python:3.11-slim",
        use_docker: bool = True,
        store: SqliteWorkspaceStore | None = None,
    ) -> None:
        workspace_root = base_dir or "backend/data/workspaces"
        self._base_dir = Path(workspace_root)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._sandbox_image = sandbox_image
        self._use_docker = use_docker
        self._store = store
        self._sessions: dict[str, WorkspaceSessionRecord] = {}
        self._lock = asyncio.Lock()
        self._runtime_prepare_lock = asyncio.Lock()
        self._runtime_prepare_task: Optional[asyncio.Task[None]] = None

    def start_runtime_prepare(self) -> None:
        if not self._use_docker:
            return
        task = self._runtime_prepare_task
        if task is not None and not task.done():
            return
        self._runtime_prepare_task = asyncio.create_task(self._prepare_runtime_task())

    async def _prepare_runtime_task(self) -> None:
        try:
            await self.prepare_runtime()
        except WorkspaceRuntimeError:
            return

    async def prepare_runtime(self) -> None:
        if not self._use_docker:
            return

        async with self._runtime_prepare_lock:
            docker_path = shutil.which("docker")
            if docker_path is None:
                raise WorkspaceRuntimeError(
                    status_code=503,
                    detail={
                        "message": "Docker is required for the workspace runtime.",
                        "issues": ["Install Docker Desktop and ensure `docker` is on PATH."],
                    },
                )

            inspect = await asyncio.to_thread(
                subprocess.run,
                [
                    docker_path,
                    "image",
                    "inspect",
                    self._sandbox_image,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if inspect.returncode == 0:
                return

            pull_process = await asyncio.create_subprocess_exec(
                docker_path,
                "pull",
                self._sandbox_image,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _stdout, stderr = await pull_process.communicate()
            if pull_process.returncode != 0:
                issue = stderr.decode("utf-8", errors="replace").strip()
                raise WorkspaceRuntimeError(
                    status_code=503,
                    detail={
                        "message": "Workspace Docker image could not be prepared.",
                        "issues": [issue or f"Unable to pull {self._sandbox_image}."],
                    },
                )

    def health_snapshot(self) -> dict[str, Any]:
        if not self._use_docker:
            return {
                "ready": True,
                "runtime_mode": "local",
                "docker_cli_available": False,
                "docker_daemon_reachable": False,
                "message": "Workspace runtime is using the local Python process.",
                "issues": [],
            }

        docker_path = shutil.which("docker")
        if docker_path is None:
            return {
                "ready": False,
                "runtime_mode": "docker",
                "docker_cli_available": False,
                "docker_daemon_reachable": False,
                "message": "Docker CLI is not installed.",
                "issues": ["Install Docker Desktop and ensure `docker` is available on PATH."],
            }

        try:
            result = subprocess.run(
                [docker_path, "info", "--format", "{{.ServerVersion}}"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as error:
            return {
                "ready": False,
                "runtime_mode": "docker",
                "docker_cli_available": True,
                "docker_daemon_reachable": False,
                "message": "Docker CLI is installed, but the daemon could not be queried.",
                "issues": [str(error)],
            }

        if result.returncode != 0:
            issue = result.stderr.strip() or result.stdout.strip() or "Unknown Docker error."
            return {
                "ready": False,
                "runtime_mode": "docker",
                "docker_cli_available": True,
                "docker_daemon_reachable": False,
                "message": "Docker Desktop is not running.",
                "issues": [issue],
            }

        task = self._runtime_prepare_task
        if task is not None and not task.done():
            return {
                "ready": False,
                "runtime_mode": "docker",
                "docker_cli_available": True,
                "docker_daemon_reachable": True,
                "docker_server_version": result.stdout.strip(),
                "message": "Workspace runtime is warming the Docker image.",
                "issues": [f"Preparing {self._sandbox_image}. Try again in a moment."],
            }

        return {
            "ready": True,
            "runtime_mode": "docker",
            "docker_cli_available": True,
            "docker_daemon_reachable": True,
            "docker_server_version": result.stdout.strip(),
            "message": "Workspace runtime is ready.",
            "issues": [],
        }

    async def create_session(self, lesson_id: str) -> dict[str, Any]:
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            raise WorkspaceRuntimeError(
                status_code=404,
                detail=f"Unknown lesson '{lesson_id}'.",
            )

        await self.prepare_runtime()

        session_id = uuid4().hex
        workspace_dir = Path(mkdtemp(prefix=f"workspace_{session_id}_", dir=self._base_dir))
        self._write_workspace_files(workspace_dir, lesson)
        process, runtime_mode = await self._start_console_process(workspace_dir)
        session = WorkspaceSessionRecord(
            session_id=session_id,
            lesson_id=lesson_id,
            workspace_dir=workspace_dir,
            visible_files=["script.py"],
            file_versions={"script.py": 1},
            console_process=process,
            runtime_mode=runtime_mode,
        )
        session.reader_task = asyncio.create_task(self._read_console_events(session))

        async with self._lock:
            self._sessions[session_id] = session
        self._persist_session(session)

        # Give the helper process a short chance to emit its ready event.
        for _ in range(5):
            if session.console_ready:
                break
            await asyncio.sleep(0.02)

        return self._session_snapshot(session)

    async def get_session(self, session_id: str) -> dict[str, Any]:
        session = await self._get_session_record(session_id)
        return self._session_snapshot(session)

    async def read_file(self, session_id: str, path: str) -> dict[str, Any]:
        session = await self._get_session_record(session_id)
        target_path = self._resolve_visible_file(session, path)
        content = target_path.read_text(encoding="utf-8")
        return {
            "path": path,
            "content": content,
            "version": session.file_versions.get(path, 1),
            "diagnostics": self._diagnostics_for_content(content, session.lesson_id),
        }

    async def write_file(self, session_id: str, path: str, content: str) -> dict[str, Any]:
        session = await self._get_session_record(session_id)
        target_path = self._resolve_visible_file(session, path)
        target_path.write_text(content, encoding="utf-8")
        session.file_versions[path] = session.file_versions.get(path, 1) + 1
        self._persist_session(session)
        diagnostics = self._diagnostics_for_content(content, session.lesson_id)
        event = {
            "type": "diagnostics",
            "path": path,
            "diagnostics": diagnostics,
            "version": session.file_versions[path],
        }
        await self._broadcast(session, event)
        return {
            "path": path,
            "content": content,
            "version": session.file_versions[path],
            "diagnostics": diagnostics,
        }

    async def run_script(self, session_id: str) -> dict[str, Any]:
        session = await self._get_session_record(session_id)
        run_id = uuid4().hex
        record = WorkspaceRunRecord(run_id=run_id, status="running")
        session.runs[run_id] = record
        self._persist_run(session.session_id, record)
        await self._send_console_command(
            session,
            {
                "type": "run_script",
                "path": "script.py",
                "run_id": run_id,
            },
        )
        return self._run_snapshot(record)

    async def get_run(self, session_id: str, run_id: str) -> dict[str, Any]:
        session = await self._get_session_record(session_id)
        record = session.runs.get(run_id)
        if record is None:
            raise WorkspaceRuntimeError(
                status_code=404,
                detail=f"Unknown run_id '{run_id}'.",
            )
        return self._run_snapshot(record)

    async def handle_console_message(self, session_id: str, message: str) -> None:
        session = await self._get_session_record(session_id)
        parsed_line = message
        try:
            payload = json.loads(message)
            parsed_line = str(payload.get("line", ""))
        except json.JSONDecodeError:
            parsed_line = message
        await self._send_console_command(
            session,
            {
                "type": "input",
                "line": parsed_line,
            },
        )

    async def subscribe(self, session_id: str) -> asyncio.Queue[dict[str, Any]]:
        session = await self._get_session_record(session_id)
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        session.listeners.add(queue)
        await queue.put({"type": "ready", "session_id": session.session_id})
        await queue.put({"type": "prompt", "prompt": session.last_prompt})
        return queue

    async def unsubscribe(self, session_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        session = await self._get_session_record(session_id)
        session.listeners.discard(queue)

    async def _get_session_record(self, session_id: str) -> WorkspaceSessionRecord:
        async with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise WorkspaceRuntimeError(
                status_code=404,
                detail=f"Unknown session_id '{session_id}'.",
            )
        return session

    def _write_workspace_files(self, workspace_dir: Path, lesson: Any) -> None:
        (workspace_dir / "script.py").write_text(
            lesson.starter_code + "\n",
            encoding="utf-8",
        )
        (workspace_dir / "tests.py").write_text(
            "\n".join(
                [
                    f"# Hidden lesson support for {lesson.id}",
                    f"REQUIRED_FUNCTION = {lesson.required_function!r}",
                    f"LESSON_ID = {lesson.id!r}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (workspace_dir / "lesson_metadata.json").write_text(
            json.dumps(
                {
                    "lesson_id": lesson.id,
                    "title": lesson.title,
                    "required_function": lesson.required_function,
                }
            ),
            encoding="utf-8",
        )
        (workspace_dir / CONSOLE_HELPER_FILENAME).write_text(
            CONSOLE_HELPER_SOURCE + "\n",
            encoding="utf-8",
        )

    async def _start_console_process(self, workspace_dir: Path) -> tuple[Process, str]:
        command, runtime_mode = self._console_command(workspace_dir)
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(workspace_dir),
            )
            return process, runtime_mode
        except FileNotFoundError as error:
            raise WorkspaceRuntimeError(
                status_code=503,
                detail={
                    "message": "Workspace runtime unavailable.",
                    "issues": [str(error)],
                },
            ) from error

    def _console_command(self, workspace_dir: Path) -> tuple[list[str], str]:
        helper_path = f"/workspace/{CONSOLE_HELPER_FILENAME}"
        if self._use_docker:
            docker_path = shutil.which("docker")
            if docker_path is None:
                raise WorkspaceRuntimeError(
                    status_code=503,
                    detail={
                        "message": "Docker is required for the workspace runtime.",
                        "issues": ["Install Docker Desktop and ensure `docker` is on PATH."],
                    },
                )
            return (
                [
                    docker_path,
                    "run",
                    "--rm",
                    "-i",
                    "--network",
                    "none",
                    "--cpus",
                    "1",
                    "--memory",
                    "256m",
                    "-v",
                    f"{workspace_dir}:/workspace",
                    "-w",
                    "/workspace",
                    self._sandbox_image,
                    "python",
                    "-u",
                    helper_path,
                ],
                "docker",
            )

        return (
            [
                sys.executable,
                "-u",
                str(workspace_dir / CONSOLE_HELPER_FILENAME),
            ],
            "local",
        )

    async def _read_console_events(self, session: WorkspaceSessionRecord) -> None:
        if session.console_process.stdout is None:
            return

        while True:
            line = await session.console_process.stdout.readline()
            if not line:
                await self._broadcast(
                    session,
                    {
                        "type": "stderr",
                        "data": "Console session ended.\n",
                    },
                )
                return

            raw = line.decode("utf-8", errors="replace").strip()
            if not raw:
                continue

            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                event = {
                    "type": "stderr",
                    "data": raw + "\n",
                }

            event_type = event.get("type")
            if event_type == "ready":
                session.console_ready = True
                self._persist_session(session)
            elif event_type == "prompt":
                session.last_prompt = str(event.get("prompt", ">>> "))
            elif event_type == "run_started":
                run_id = str(event.get("run_id", ""))
                record = session.runs.get(run_id)
                if record is not None:
                    record.status = "running"
                    self._persist_run(session.session_id, record)
            elif event_type in {"run_finished", "run_failed"}:
                run_id = str(event.get("run_id", ""))
                record = session.runs.get(run_id)
                if record is not None:
                    record.status = "failed" if event_type == "run_failed" else "completed"
                    record.exit_code = int(event.get("exit_code", 0))
                    record.finished_at = datetime.now(timezone.utc).isoformat()
                    self._persist_run(session.session_id, record)

            await self._broadcast(session, event)

    async def _send_console_command(
        self,
        session: WorkspaceSessionRecord,
        payload: dict[str, Any],
    ) -> None:
        if session.console_process.stdin is None or session.console_process.returncode is not None:
            raise WorkspaceRuntimeError(
                status_code=503,
                detail={
                    "message": "Console session is not available.",
                    "issues": ["Create a new workspace session and try again."],
                },
            )
        session.console_process.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
        await session.console_process.stdin.drain()

    async def _broadcast(
        self,
        session: WorkspaceSessionRecord,
        event: dict[str, Any],
    ) -> None:
        dead_queues: list[asyncio.Queue[dict[str, Any]]] = []
        for queue in session.listeners:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                dead_queues.append(queue)
        for queue in dead_queues:
            session.listeners.discard(queue)

    def _resolve_visible_file(self, session: WorkspaceSessionRecord, path: str) -> Path:
        if path not in session.visible_files:
            raise WorkspaceRuntimeError(
                status_code=404,
                detail=f"Unknown visible file '{path}'.",
            )
        return session.workspace_dir / path

    def _session_snapshot(self, session: WorkspaceSessionRecord) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "lesson_id": session.lesson_id,
            "visible_files": session.visible_files,
            "console_ready": session.console_ready,
            "runtime_mode": session.runtime_mode,
        }

    def _run_snapshot(self, record: WorkspaceRunRecord) -> dict[str, Any]:
        return {
            "run_id": record.run_id,
            "status": record.status,
            "exit_code": record.exit_code,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
        }

    def _diagnostics_for_content(
        self,
        content: str,
        lesson_id: str,
    ) -> list[dict[str, Any]]:
        diagnostics = self._syntax_diagnostics(content)
        lesson = get_lesson_definition(lesson_id)
        if lesson is not None:
            diagnostics.extend(build_blank_diagnostics(content, lesson))
        return diagnostics

    def _syntax_diagnostics(self, content: str) -> list[dict[str, Any]]:
        try:
            ast.parse(content)
        except SyntaxError as error:
            return [
                {
                    "message": error.msg,
                    "line": error.lineno or 1,
                    "column": error.offset or 1,
                    "severity": "error",
                }
            ]
        return []

    def persisted_session_snapshot(self, session_id: str) -> dict[str, Any] | None:
        if self._store is None:
            return None
        return self._store.get_session(session_id)

    def persisted_run_snapshot(self, session_id: str, run_id: str) -> dict[str, Any] | None:
        if self._store is None:
            return None
        return self._store.get_run(session_id, run_id)

    def record_artifact_reference(
        self,
        *,
        owner_kind: str,
        owner_id: str,
        artifact_kind: str,
        artifact_path: str,
    ) -> None:
        if self._store is None:
            return
        self._store.record_artifact(
            owner_kind=owner_kind,
            owner_id=owner_id,
            artifact_kind=artifact_kind,
            artifact_path=artifact_path,
        )

    def list_artifact_references(self, owner_kind: str, owner_id: str) -> list[dict[str, Any]]:
        if self._store is None:
            return []
        return self._store.list_artifacts(owner_kind, owner_id)

    def _persist_session(self, session: WorkspaceSessionRecord) -> None:
        if self._store is None:
            return
        self._store.upsert_session(
            session_id=session.session_id,
            lesson_id=session.lesson_id,
            workspace_dir=str(session.workspace_dir),
            visible_files=session.visible_files,
            file_versions=session.file_versions,
            runtime_mode=session.runtime_mode,
            console_ready=session.console_ready,
        )

    def _persist_run(self, session_id: str, record: WorkspaceRunRecord) -> None:
        if self._store is None:
            return
        self._store.upsert_run(
            session_id=session_id,
            run_id=record.run_id,
            status=record.status,
            exit_code=record.exit_code,
            started_at=record.started_at,
            finished_at=record.finished_at,
        )

    def close(self) -> None:
        for session in list(self._sessions.values()):
            if session.reader_task is not None:
                session.reader_task.cancel()
            if session.console_process.returncode is None:
                session.console_process.terminate()
