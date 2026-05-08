from __future__ import annotations

from backend.workspace_store_sqlite import SqliteWorkspaceStore


def test_session_metadata_persists_and_reloads(tmp_path):
    store = SqliteWorkspaceStore(str(tmp_path / "workspace_state.db"))

    store.upsert_session(
        session_id="session-1",
        lesson_id="dp_policy_eval",
        workspace_dir="/tmp/workspace-1",
        visible_files=["script.py"],
        file_versions={"script.py": 2},
        runtime_mode="docker",
        console_ready=True,
    )

    snapshot = store.get_session("session-1")

    assert snapshot is not None
    assert snapshot["lesson_id"] == "dp_policy_eval"
    assert snapshot["file_versions"]["script.py"] == 2


def test_run_metadata_persists_and_reloads(tmp_path):
    store = SqliteWorkspaceStore(str(tmp_path / "workspace_state.db"))

    store.upsert_run(
        session_id="session-1",
        run_id="run-1",
        status="completed",
        exit_code=0,
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:02+00:00",
    )

    snapshot = store.get_run("session-1", "run-1")

    assert snapshot is not None
    assert snapshot["status"] == "completed"
    assert snapshot["exit_code"] == 0


def test_artifact_references_are_recorded_and_queryable(tmp_path):
    store = SqliteWorkspaceStore(str(tmp_path / "workspace_state.db"))

    store.record_artifact(
        owner_kind="session",
        owner_id="session-1",
        artifact_kind="replay_video",
        artifact_path="/tmp/replay.mp4",
    )

    rows = store.list_artifacts("session", "session-1")

    assert rows == [
        {
            "owner_kind": "session",
            "owner_id": "session-1",
            "artifact_kind": "replay_video",
            "artifact_path": "/tmp/replay.mp4",
            "created_at_utc": rows[0]["created_at_utc"],
        }
    ]
