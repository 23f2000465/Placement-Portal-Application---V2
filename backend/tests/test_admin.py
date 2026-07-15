import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from extensions import db
from init_db import seed_admin
from models import Company, User


class AdminTests(unittest.TestCase):
    def setUp(self):
        file = tempfile.NamedTemporaryFile(suffix=".db", delete=False); file.close(); self.path = file.name
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.path}", "SECRET_KEY": "test"})
        self.context = self.app.app_context(); self.context.push(); db.create_all()
        seed_admin("admin@test.com", "admin123")
        company_user = User(email="company@test.com", role="Company"); company_user.set_password("secret1")
        company_user.company = Company(name="Simple Tech", industry="IT", location="Delhi", hr_contact="9000000000")
        db.session.add(company_user); db.session.commit(); self.company = company_user.company
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.context.pop(); os.unlink(self.path)

    def test_only_admin_can_approve_company(self):
        self.client.post("/api/auth/login", json={"email": "company@test.com", "password": "secret1"})
        self.assertEqual(self.client.patch(f"/api/admin/companies/{self.company.id}/status", json={"status": "Approved"}).status_code, 403)
        self.client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
        response = self.client.patch(f"/api/admin/companies/{self.company.id}/status", json={"status": "Approved"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(db.session.get(Company, self.company.id).approval_status, "Approved")

    def test_dashboard_and_search(self):
        self.client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
        self.assertEqual(self.client.get("/api/admin/dashboard").get_json()["companies"], 1)
        self.assertEqual(len(self.client.get("/api/admin/companies?q=Simple").get_json()["companies"]), 1)


if __name__ == "__main__": unittest.main()
