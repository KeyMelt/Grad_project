import unittest

from backend.logger.event_logger import EventLogger


class EventLoggerTest(unittest.TestCase):
    def test_end_episode_snapshots_current_steps(self):
        logger = EventLogger(log_dir="backend/logger/logs")

        logger.log_step({"state": 0, "reward": 1})
        logger.end_episode()
        logger.log_step({"state": 1, "reward": 2})
        logger.end_episode()

        logs = logger.get_logs()

        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0][0]["state"], 0)
        self.assertEqual(logs[1][0]["state"], 1)

    def test_clear_resets_all_in_memory_state(self):
        logger = EventLogger(log_dir="backend/logger/logs")

        logger.log_step({"state": 0})
        logger.end_episode()
        logger.clear()

        self.assertEqual(logger.get_logs(), [])


if __name__ == "__main__":
    unittest.main()
