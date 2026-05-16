from __future__ import annotations

import asyncio

import pytest

from backend.services.workspace_service import WorkspaceRuntimeError, WorkspaceSessionService
from backend.workspace_store_sqlite import SqliteWorkspaceStore


async def _cleanup_service(service: WorkspaceSessionService) -> None:
    for session in service._sessions.values():  # noqa: SLF001
        if session.reader_task is not None:
            session.reader_task.cancel()
        if session.console_process.returncode is None:
            session.console_process.terminate()
            await session.console_process.wait()


@pytest.mark.anyio
async def test_workspace_session_creates_visible_and_hidden_files(tmp_path):
    service = WorkspaceSessionService(base_dir=str(tmp_path), use_docker=False)

    try:
        session = await service.create_session(
            "dp_policy_eval",
            owner_user_id="student-1",
            owner_role="student",
        )
        assert session["lesson_id"] == "dp_policy_eval"
        assert session["visible_files"] == ["script.py"]
        assert session["runtime_mode"] == "local"

        file_snapshot = await service.read_file(session["session_id"], "script.py")
        assert "def policy_evaluation" in file_snapshot["content"]
        assert any(
            "Bellman expectation update" in diagnostic["message"]
            for diagnostic in file_snapshot["diagnostics"]
        )

        session_record = service._sessions[session["session_id"]]  # noqa: SLF001
        assert (session_record.workspace_dir / "tests.py").exists()
        assert (session_record.workspace_dir / "lesson_metadata.json").exists()
    finally:
        await _cleanup_service(service)


@pytest.mark.anyio
async def test_workspace_service_requires_docker_when_enabled(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr("backend.services.workspace_service.shutil.which", lambda name: None)
    service = WorkspaceSessionService(base_dir=str(tmp_path), use_docker=True)

    with pytest.raises(WorkspaceRuntimeError) as error:
        await service.create_session(
            "dp_policy_eval",
            owner_user_id="student-1",
            owner_role="student",
        )

    assert "Docker is required for the workspace runtime." in str(error.value)


@pytest.mark.anyio
async def test_workspace_run_executes_script_and_tracks_completion(tmp_path):
    service = WorkspaceSessionService(
        base_dir=str(tmp_path),
        use_docker=False,
        store=SqliteWorkspaceStore(str(tmp_path / "workspace_state.db")),
    )

    try:
        session = await service.create_session(
            "dp_policy_eval",
            owner_user_id="student-1",
            owner_role="student",
        )
        await service.write_file(
            session["session_id"],
            "script.py",
            "print('workspace-ok')\n",
        )
        run = await service.run_script(session["session_id"])

        for _ in range(20):
            snapshot = await service.get_run(session["session_id"], run["run_id"])
            if snapshot["status"] == "completed":
                break
            await asyncio.sleep(0.05)
        else:
            raise AssertionError("Workspace run did not reach completion in time.")

        assert snapshot["exit_code"] == 0
        persisted_session = service.persisted_session_snapshot(session["session_id"])
        assert persisted_session is not None
        assert persisted_session["lesson_id"] == "dp_policy_eval"

        persisted_run = service.persisted_run_snapshot(session["session_id"], run["run_id"])
        assert persisted_run is not None
        assert persisted_run["status"] == "completed"
    finally:
        await _cleanup_service(service)


@pytest.mark.anyio
async def test_workspace_store_records_artifact_references(tmp_path):
    service = WorkspaceSessionService(
        base_dir=str(tmp_path),
        use_docker=False,
        store=SqliteWorkspaceStore(str(tmp_path / "workspace_state.db")),
    )

    try:
        session = await service.create_session(
            "dp_policy_eval",
            owner_user_id="student-1",
            owner_role="student",
        )
        service.record_artifact_reference(
            owner_kind="session",
            owner_id=session["session_id"],
            artifact_kind="replay_video",
            artifact_path="/tmp/replay.mp4",
        )

        artifacts = service.list_artifact_references("session", session["session_id"])

        assert artifacts[0]["artifact_kind"] == "replay_video"
        assert artifacts[0]["artifact_path"] == "/tmp/replay.mp4"
    finally:
        await _cleanup_service(service)
