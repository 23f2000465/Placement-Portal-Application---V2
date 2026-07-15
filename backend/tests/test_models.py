import os
import sys
import tempfile
import unittest

from sqlalchemy.exc import IntegrityError

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from extensions import db
from init_db import seed_admin
from models import Application, Company, Drive, Student, User


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.database_file.close()
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.database_file.name}",
        })
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
        os.unlink(self.database_file.name)

    def create_records(self):
        company_user = User(email="company@test.com", role="Company")
        company_user.set_password("test-password")
        student_user = User(email="student@test.com", role="Student")
        student_user.set_password("test-password")
        db.session.add_all([company_user, student_user])
        db.session.flush()

        company = Company(user_id=company_user.id, name="Test Ltd", industry="IT", location="Chennai", hr_contact="9999999999", approval_status="Approved")
        student = Student(user_id=student_user.id, full_name="Test Student", student_code="ST001", contact="8888888888", branch="CSE", cgpa=8.0, graduation_year=2027)
        db.session.add_all([company, student])
        db.session.flush()

        from datetime import datetime
        drive = Drive(company_id=company.id, title="Developer", description="Build software", required_skills="Python", salary=500000, eligible_branch="CSE", minimum_cgpa=7, graduation_year=2027, application_deadline=datetime(2027, 1, 1), status="Approved")
        db.session.add(drive)
        db.session.commit()
        return student, drive

    def test_admin_is_seeded_once_and_password_is_hashed(self):
        first = seed_admin("admin@test.com", "secret123")
        second = seed_admin("other@test.com", "other-secret")
        self.assertEqual(first.id, second.id)
        self.assertNotEqual(first.password_hash, "secret123")
        self.assertTrue(first.check_password("secret123"))
        self.assertEqual(User.query.filter_by(role="Admin").count(), 1)

    def test_duplicate_application_is_blocked(self):
        student, drive = self.create_records()
        db.session.add(Application(student_id=student.id, drive_id=drive.id))
        db.session.commit()
        db.session.add(Application(student_id=student.id, drive_id=drive.id))
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_relationships_work(self):
        student, drive = self.create_records()
        application = Application(student_id=student.id, drive_id=drive.id)
        db.session.add(application)
        db.session.commit()
        self.assertEqual(application.student.full_name, "Test Student")
        self.assertEqual(application.drive.company.name, "Test Ltd")


if __name__ == "__main__":
    unittest.main()
