import unittest
from app.services.skill_extractor import extract_skills_from_text
from app.services.resume_parser import ResumeParser

class ResumeTestCase(unittest.TestCase):
    def test_skill_extractor(self):
        text = "Experienced in Python, Machine Learning, Docker, SQL, and Flask microservices."
        skills = extract_skills_from_text(text)
        skill_names = [s['name'] for s in skills]
        
        self.assertIn('Python', skill_names)
        self.assertIn('Machine Learning', skill_names)
        self.assertIn('Docker', skill_names)
        self.assertIn('SQL', skill_names)
        self.assertIn('Flask', skill_names)

    def test_parser_heuristics(self):
        text = "John Doe john.doe@example.com +1-555-123-4567 5 years of experience B.Tech Computer Science"
        email = ResumeParser.parse_email(text)
        phone = ResumeParser.parse_phone(text)
        exp_years = ResumeParser.parse_experience_years(text)
        
        self.assertEqual(email, 'john.doe@example.com')
        self.assertIsNotNone(phone)
        self.assertEqual(exp_years, 5.0)

if __name__ == '__main__':
    unittest.main()
