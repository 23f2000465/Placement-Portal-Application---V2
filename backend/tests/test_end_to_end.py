import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from extensions import db
from init_db import seed_admin


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        file.close()
        self.path = file.name
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.path}", "SECRET_KEY": "test"})
        self.context = self.app.app_context(); self.context.push(); db.create_all()
        seed_admin("admin@test.com", "admin123")
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.context.pop(); os.unlink(self.path)
        for folder_name in ["exports", "reports"]:
            folder = Path(os.path.dirname(os.path.dirname(__file__))) / folder_name
            if folder.exists():
                for file in folder.iterdir(): file.unlink()
                folder.rmdir()

    def login(self, email, password="secret1"):
        return self.client.post("/api/auth/login", json={"email": email, "password": password})

    def test_complete_admin_company_student_flow(self):
        company = {"email": "company@test.com", "password": "secret1", "name": "Campus Tech", "industry": "IT", "location": "Chennai", "hr_contact": "9000000000"}
        student = {"email": "student@test.com", "password": "secret1", "full_name": "Demo Student", "student_code": "DS001", "contact": "8000000000", "branch": "CSE", "cgpa": 8.2, "graduation_year": 2027}
        self.assertEqual(self.client.post("/api/auth/register/company", json=company).status_code, 201)
        self.assertEqual(self.client.post("/api/auth/register/student", json=student).status_code, 201)

        self.login(company["email"])
        drive_data = {"title": "Flask Developer", "description": "Build simple APIs", "required_skills": "Python, Flask", "salary": 600000, "eligible_branch": "CSE", "minimum_cgpa": 7, "graduation_year": 2027, "application_deadline": "2027-01-01T10:00"}
        self.assertEqual(self.client.post("/api/company/drives", json=drive_data).status_code, 403)

        self.login("admin@test.com", "admin123")
        company_id = self.client.get("/api/admin/companies").get_json()["companies"][0]["id"]
        self.client.patch(f"/api/admin/companies/{company_id}/status", json={"status": "Approved"})

        self.login(company["email"])
        drive_response = self.client.post("/api/company/drives", json=drive_data)
        self.assertEqual(drive_response.status_code, 201)
        drive_id = drive_response.get_json()["drive"]["id"]

        self.login("admin@test.com", "admin123")
        self.client.patch(f"/api/admin/drives/{drive_id}/status", json={"status": "Approved"})

        self.login(student["email"])
        self.assertEqual(len(self.client.get("/api/student/drives?q=Flask").get_json()["drives"]), 1)
        apply_response = self.client.post(f"/api/student/drives/{drive_id}/apply")
        self.assertEqual(apply_response.status_code, 201)
        application_id = apply_response.get_json()["application"]["id"]
        self.assertEqual(self.client.post(f"/api/student/drives/{drive_id}/apply").status_code, 409)

        self.login(company["email"])
        self.assertEqual(self.client.post(f"/api/company/applications/{application_id}/interview", json={"scheduled_at": "2026-12-15T10:00", "mode": "Online", "meeting_details": "https://meet.example/test"}).status_code, 200)
        self.assertEqual(self.client.patch(f"/api/company/applications/{application_id}", json={"status": "Selected", "feedback": "Good skills"}).status_code, 200)

        self.login(student["email"])
        self.assertEqual(self.client.get("/api/student/applications").get_json()["applications"][0]["status"], "Selected")
        self.assertEqual(len(self.client.get("/api/student/placements").get_json()["placements"]), 1)
        export = self.client.post("/api/student/exports")
        job_id = export.get_json()["job_id"]
        self.assertEqual(self.client.get(f"/api/student/exports/{job_id}").get_json()["status"], "Completed")


if __name__ == "__main__":
    unittest.main()
