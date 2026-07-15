import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from extensions import db
from models import Company, User


class CompanyTests(unittest.TestCase):
    def setUp(self):
        f=tempfile.NamedTemporaryFile(suffix='.db',delete=False); f.close(); self.path=f.name
        self.app=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':f'sqlite:///{self.path}','SECRET_KEY':'test'}); self.ctx=self.app.app_context(); self.ctx.push(); db.create_all()
        user=User(email='company@test.com',role='Company'); user.set_password('secret1'); user.company=Company(name='Company',industry='IT',location='Pune',hr_contact='9000000000'); db.session.add(user); db.session.commit(); self.company=user.company
        self.client=self.app.test_client(); self.client.post('/api/auth/login',json={'email':'company@test.com','password':'secret1'})
        self.data={'title':'Developer','description':'Build app','required_skills':'Python','salary':500000,'eligible_branch':'CSE','minimum_cgpa':7,'graduation_year':2027,'application_deadline':'2027-01-01T10:00'}
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop(); os.unlink(self.path)
    def test_pending_company_gets_403(self):
        self.assertEqual(self.client.post('/api/company/drives',json=self.data).status_code,403)
    def test_approved_company_can_create_and_manage_drive(self):
        self.company.approval_status='Approved'; db.session.commit()
        response=self.client.post('/api/company/drives',json=self.data)
        self.assertEqual(response.status_code,201)
        drive_id=response.get_json()['drive']['id']
        self.assertEqual(self.client.get('/api/company/drives').get_json()['drives'][0]['title'],'Developer')
        self.assertEqual(self.client.patch(f'/api/company/drives/{drive_id}',json={'title':'Junior Developer'}).status_code,200)

if __name__=='__main__': unittest.main()
