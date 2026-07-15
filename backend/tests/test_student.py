import os, sys, tempfile, unittest
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from extensions import db
from models import Company, Drive, Student, User


class StudentTests(unittest.TestCase):
    def setUp(self):
        f=tempfile.NamedTemporaryFile(suffix='.db',delete=False); f.close(); self.path=f.name
        self.app=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':f'sqlite:///{self.path}','SECRET_KEY':'test'}); self.ctx=self.app.app_context(); self.ctx.push(); db.create_all()
        cu=User(email='c@test.com',role='Company'); cu.set_password('secret1'); cu.company=Company(name='Tech',industry='IT',location='Delhi',hr_contact='9000000000',approval_status='Approved')
        su=User(email='s@test.com',role='Student'); su.set_password('secret1'); su.student=Student(full_name='Student',student_code='S1',contact='8000000000',branch='CSE',cgpa=8,graduation_year=2027)
        db.session.add_all([cu,su]); db.session.flush(); self.student=su.student
        self.drive=Drive(company_id=cu.company.id,title='Developer',description='Job',required_skills='Python',salary=5,eligible_branch='CSE',minimum_cgpa=7,graduation_year=2027,application_deadline=datetime(2027,1,1),status='Approved')
        self.ineligible=Drive(company_id=cu.company.id,title='Analyst',description='Job',required_skills='Excel',salary=5,eligible_branch='EE',minimum_cgpa=9,graduation_year=2027,application_deadline=datetime(2027,1,1),status='Approved')
        db.session.add_all([self.drive,self.ineligible]); db.session.commit(); self.client=self.app.test_client(); self.client.post('/api/auth/login',json={'email':'s@test.com','password':'secret1'})
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop(); os.unlink(self.path)
    def test_eligibility_and_duplicate_validation(self):
        self.assertEqual(self.client.post(f'/api/student/drives/{self.ineligible.id}/apply').status_code,400)
        self.assertEqual(self.client.post(f'/api/student/drives/{self.drive.id}/apply').status_code,201)
        self.assertEqual(self.client.post(f'/api/student/drives/{self.drive.id}/apply').status_code,409)
    def test_search_and_profile(self):
        self.assertEqual(len(self.client.get('/api/student/drives?q=Python').get_json()['drives']),1)
        self.assertEqual(self.client.patch('/api/student/profile',json={'skills':'Python, Flask'}).status_code,200)

if __name__=='__main__': unittest.main()
