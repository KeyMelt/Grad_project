from __future__ import annotations

import asyncio

import pytest

from backend.services.workspace_service import WorkspaceRuntimeError, WorkspaceSessionService


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
        session = await service.create_session("dp_policy_eval")
        assert session["lesson_id"] == "dp_policy_eval"
        assert session["visible_files"] == ["script.py"]
        assert session["runtime_mode"] == "local"

        file_snapshot = await service.read_file(session["session_id"], "script.py")
        assert "def policy_evaluation" in file_snapshot["content"]

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
        await service.create_session("dp_policy_eval")

    assert "Docker is required for the workspace runtime." in str(error.value)


@pytest.mark.anyio
async def test_workspace_run_executes_script_and_tracks_completion(tmp_path):
    service = WorkspaceSessionService(base_dir=str(tmp_path), use_docker=False)

    try:
        session = await service.create_session("dp_policy_eval")
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
    finally:
        await _cleanup_service(service)
