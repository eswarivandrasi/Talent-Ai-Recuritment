import unittest
from app import create_app
from app.models import db, User, Candidate, Recruiter

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_registration_candidate(self):
        response = self.client.post('/register', data={
            'email': 'newcandidate@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'candidate',
            'full_name': 'Test Candidate'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='newcandidate@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'candidate')
        self.assertEqual(user.candidate_profile.full_name, 'Test Candidate')

    def test_login_and_role_protection(self):
        # Register recruiter
        self.client.post('/register', data={
            'email': 'recruiter1@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'recruiter',
            'company_name': 'Tech Inc'
        })

        # Login
        response = self.client.post('/login', data={
            'email': 'recruiter1@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Recruiter Dashboard', response.data)

        # Attempt to access Candidate dashboard -> should be redirected (403 forbidden logic)
        cand_resp = self.client.get('/candidate/dashboard', follow_redirects=True)
        self.assertIn(b'Recruiter Dashboard', cand_resp.data)

if __name__ == '__main__':
    unittest.main()
