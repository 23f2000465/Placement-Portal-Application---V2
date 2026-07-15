import os, sys, tempfile, unittest
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from extensions import db
from models import Application, Company, Drive, Student, User


class HistoryTests(unittest.TestCase):
    def setUp(self):
        f=tempfile.NamedTemporaryFile(suffix='.db',delete=False); f.close(); self.path=f.name
        self.app=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':f'sqlite:///{self.path}','SECRET_KEY':'test'}); self.ctx=self.app.app_context(); self.ctx.push(); db.create_all()
        cu=User(email='c@test.com',role='Company'); cu.set_password('secret1'); cu.company=Company(name='Tech',industry='IT',location='Delhi',hr_contact='9',approval_status='Approved')
        su=User(email='s@test.com',role='Student'); su.set_password('secret1'); su.student=Student(full_name='Student',student_code='S1',contact='8',branch='CSE',cgpa=8,graduation_year=2027)
        db.session.add_all([cu,su]); db.session.flush(); drive=Drive(company_id=cu.company.id,title='Developer',description='Job',required_skills='Python',salary=500000,eligible_branch='CSE',minimum_cgpa=7,graduation_year=2027,application_deadline=datetime(2027,1,1),status='Approved'); db.session.add(drive); db.session.flush(); self.application=Application(student_id=su.student.id,drive_id=drive.id); db.session.add(self.application); db.session.commit(); self.client=self.app.test_client()
    def tearDown(self): db.session.remove(); db.drop_all(); self.ctx.pop(); os.unlink(self.path)
    def test_selected_application_creates_student_placement(self):
        self.client.post('/api/auth/login',json={'email':'c@test.com','password':'secret1'}); self.assertEqual(self.client.patch(f'/api/company/applications/{self.application.id}',json={'status':'Selected'}).status_code,200)
        self.client.post('/api/auth/login',json={'email':'s@test.com','password':'secret1'}); rows=self.client.get('/api/student/placements').get_json()['placements']; self.assertEqual(len(rows),1); self.assertEqual(self.client.get(f"/api/student/placements/{rows[0]['id']}/confirmation").status_code,200)

if __name__=='__main__': unittest.main()
