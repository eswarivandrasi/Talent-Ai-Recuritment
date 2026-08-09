import unittest
from app.services.interview_engine import InterviewEngine
from app.services.answer_evaluator import AnswerEvaluator

class InterviewTestCase(unittest.TestCase):
    def test_question_generation(self):
        job_skills = ['Python', 'Machine Learning']
        candidate_skills = ['Python', 'SQL']
        qs = InterviewEngine.generate_questions(job_skills, candidate_skills, question_count=5)
        
        self.assertEqual(len(qs), 5)
        self.assertTrue(any(q['category'] == 'Technical' for q in qs))

    def test_answer_evaluation(self):
        answer = "Lists in Python are mutable structures defined with square brackets, while tuples are immutable."
        keywords = ['mutable', 'immutable', 'brackets', 'tuples']
        sample_answer = "Lists are mutable and defined with square brackets. Tuples are immutable."
        
        score, feedback = AnswerEvaluator.evaluate_answer(answer, keywords, sample_answer)
        self.assertGreaterEqual(score, 70.0)
        self.assertIn('matched_keywords', feedback)

if __name__ == '__main__':
    unittest.main()
