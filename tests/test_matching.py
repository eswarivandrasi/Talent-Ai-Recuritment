import unittest
from app.services.job_matcher import JobMatcher

class JobMatcherTestCase(unittest.TestCase):
    def test_text_similarity(self):
        job_desc = "Looking for Senior Machine Learning Engineer skilled in Python PyTorch SQL"
        resume_text = "Senior ML Engineer with expertise in Python PyTorch SQL database modeling"
        
        sim_score = JobMatcher.calculate_text_similarity(resume_text, job_desc)
        self.assertGreater(sim_score, 20.0)

    def test_skill_overlap(self):
        cand_skills = ['Python', 'SQL', 'Flask', 'Machine Learning']
        req_skills = ['Python', 'SQL', 'Docker', 'AWS']
        
        ratio, matching, missing = JobMatcher.calculate_skill_overlap(cand_skills, req_skills)
        self.assertEqual(ratio, 50.0)
        self.assertIn('Python', matching)
        self.assertIn('SQL', matching)
        self.assertIn('Docker', missing)
        self.assertIn('AWS', missing)

    def test_complete_matching_pipeline(self):
        job_desc = "Python Machine Learning Engineer"
        req_skills = ['Python', 'Machine Learning', 'SQL']
        resume_text = "Expert Python and Machine Learning developer with strong SQL background"
        cand_skills = ['Python', 'Machine Learning', 'SQL']

        res = JobMatcher.match(resume_text, cand_skills, job_desc, req_skills)
        self.assertGreaterEqual(res['overall_match_score'], 80.0)
        self.assertEqual(len(res['missing_skills']), 0)

if __name__ == '__main__':
    unittest.main()
