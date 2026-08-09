import unittest
from app.services.ranking_engine import RankingEngine

class RankingTestCase(unittest.TestCase):
    def test_weighted_scoring(self):
        resume_match = 80.0
        interview_score = 90.0
        skill_match = 70.0
        experience_score = 100.0

        weights = {'resume_match': 0.40, 'interview': 0.35, 'skill_match': 0.15, 'experience': 0.10}
        
        # Formula: (80*0.4) + (90*0.35) + (70*0.15) + (100*0.1) = 32 + 31.5 + 10.5 + 10 = 84.0
        final_score, breakdown = RankingEngine.calculate_final_score(
            resume_match, interview_score, skill_match, experience_score, weights
        )
        self.assertEqual(final_score, 84.0)

    def test_skill_gap_analysis(self):
        matching = ['Python', 'SQL']
        missing = ['Docker', 'AWS']
        gap = RankingEngine.generate_skill_gap_analysis('ML Engineer', matching, missing)
        
        self.assertEqual(gap['strong_skills'], matching)
        self.assertEqual(gap['missing_skills'], missing)
        self.assertGreater(len(gap['learning_recommendations']), 0)

if __name__ == '__main__':
    unittest.main()
