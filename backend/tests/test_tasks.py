import os, sys, tempfile, unittest
from datetime import datetime
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from extensions import db
from models import Application, Company, Drive, Student, User


class TaskTests(unittest.TestCase):
    def setUp(self):
        f=tempfile.NamedTemporaryFile(suffix='.db',delete=False); f.close(); self.path=f.name
        self.app=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':f'sqlite:///{self.path}','SECRET_KEY':'test'}); self.ctx=self.app.app_context(); self.ctx.push(); db.create_all()
        cu=User(email='c@test.com',role='Company'); cu.set_password('secret1'); cu.company=Company(name='Tech',industry='IT',location='Delhi',hr_contact='9',approval_status='Approved'); su=User(email='s@test.com',role='Student'); su.set_password('secret1'); su.student=Student(full_name='Student',student_code='S1',contact='8',branch='CSE',cgpa=8,graduation_year=2027); db.session.add_all([cu,su]); db.session.flush(); drive=Drive(company_id=cu.company.id,title='Developer',description='Job',required_skills='Python',salary=5,eligible_branch='CSE',minimum_cgpa=7,graduation_year=2027,application_deadline=datetime(2027,1,1),status='Approved'); db.session.add(drive); db.session.flush(); db.session.add(Application(student_id=su.student.id,drive_id=drive.id)); db.session.commit(); self.client=self.app.test_client(); self.client.post('/api/auth/login',json={'email':'s@test.com','password':'secret1'})
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop(); os.unlink(self.path)
        for folder in ['exports','reports']:
            path=Path(os.path.dirname(os.path.dirname(__file__)))/folder
            if path.exists():
                for file in path.iterdir(): file.unlink()
                path.rmdir()
    def test_async_export_flow_in_eager_test_mode(self):
        response=self.client.post('/api/student/exports'); self.assertEqual(response.status_code,202); job_id=response.get_json()['job_id']; status=self.client.get(f'/api/student/exports/{job_id}').get_json(); self.assertEqual(status['status'],'Completed'); download=self.client.get(f'/api/student/exports/{job_id}/download'); self.assertEqual(download.status_code,200); download.close()

if __name__=='__main__': unittest.main()
