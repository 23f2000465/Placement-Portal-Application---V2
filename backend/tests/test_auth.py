import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from extensions import db
from init_db import seed_admin


class AuthTests(unittest.TestCase):
    def setUp(self):
        database = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        database.close()
        self.path = database.name
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.path}", "SECRET_KEY": "test"})
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        seed_admin("admin@test.com", "admin123")
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
        os.unlink(self.path)

    def test_student_register_login_and_session(self):
        response = self.client.post("/api/auth/register/student", json={
            "email": "student@test.com", "password": "secret1", "full_name": "A Student",
            "student_code": "ST100", "contact": "9999999999", "branch": "CSE", "cgpa": 8.5,
            "graduation_year": 2027,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "student@test.com", "password": "secret1"}).status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me").get_json()["user"]["role"], "Student")

    def test_wrong_password_and_inactive_user_are_rejected(self):
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrong"}).status_code, 401)
        self.client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
        self.assertEqual(self.client.get("/api/auth/me").status_code, 200)


if __name__ == "__main__":
    unittest.main()
