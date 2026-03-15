import unittest

from backend.job_store import ExecutionJobStore


class ExecutionJobStoreTest(unittest.TestCase):
    def test_job_lifecycle_snapshot(self):
        store = ExecutionJobStore()

        job = store.create()
        self.assertEqual(job.status, "queued")

        store.mark_running(job.task_id)
        self.assertEqual(store.snapshot(job.task_id)["status"], "running")

        result = {"status": "success", "message": "done"}
        store.mark_succeeded(job.task_id, result)

        snapshot = store.snapshot(job.task_id)
        self.assertEqual(snapshot["status"], "succeeded")
        self.assertEqual(snapshot["result"], result)

    def test_failed_job_exposes_error(self):
        store = ExecutionJobStore()
        job = store.create()

        store.mark_failed(job.task_id, {"message": "failure"})

        snapshot = store.snapshot(job.task_id)
        self.assertEqual(snapshot["status"], "failed")
        self.assertEqual(snapshot["error"], {"message": "failure"})


if __name__ == "__main__":
    unittest.main()
