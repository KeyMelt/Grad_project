import unittest

from backend.services.student_progress_service import StudentProgressService


class StudentProgressAuthTest(unittest.TestCase):
    def setUp(self):
        self.service = object.__new__(StudentProgressService)

    def test_hash_password_hashes_and_salts_without_storing_plaintext(self):
        salt, password_hash = self.service._hash_password("Password123!")

        self.assertNotEqual(password_hash, "")
        self.assertNotEqual(salt, "")
        self.assertNotEqual(password_hash, "Password123!")
        self.assertNotEqual(salt, "Password123!")
        self.assertTrue(
            self.service._verify_password(
                password="Password123!",
                stored_salt=salt,
                stored_hash=password_hash,
            )
        )

    def test_verify_password_rejects_wrong_password(self):
        salt, password_hash = self.service._hash_password("Password123!")

        self.assertFalse(
            self.service._verify_password(
                password="WrongPass123!",
                stored_salt=salt,
                stored_hash=password_hash,
            )
        )

    def test_sign_in_rejects_short_password(self):
        with self.assertRaises(ValueError):
            self.service.sign_in("Sara Ahmed", "short")


if __name__ == "__main__":
    unittest.main()
