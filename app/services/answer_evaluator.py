import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AnswerEvaluator:
    @staticmethod
    def evaluate_answer(answer_text, expected_keywords, sample_answer=None):
        """
        Evaluates candidate answer text against expected keywords and sample reference answer.
        Returns score (0-100) and feedback object.
        """
        if not answer_text or len(answer_text.strip()) < 5:
            return 0.0, {
                'relevance': 'Poor',
                'keyword_coverage': 0.0,
                'strengths': [],
                'weaknesses': ['No answer provided or answer is too short.'],
                'suggestions': ['Provide a complete response with key technical concepts.']
            }

        answer_clean = answer_text.lower()

        # 1. Keyword Coverage Evaluation
        matched_keywords = []
        missing_keywords = []
        if expected_keywords:
            for kw in expected_keywords:
                pattern = r'\b' + re.escape(kw.lower()) + r'\b'
                if re.search(pattern, answer_clean):
                    matched_keywords.append(kw)
                else:
                    missing_keywords.append(kw)
            keyword_score = (len(matched_keywords) / len(expected_keywords)) * 100.0
        else:
            keyword_score = 70.0  # Default baseline if no keywords specified

        # 2. Semantic/Text Similarity against sample answer
        similarity_score = 50.0
        if sample_answer:
            try:
                vec = TfidfVectorizer(stop_words='english')
                matrix = vec.fit_transform([sample_answer.lower(), answer_clean])
                sim = cosine_similarity(matrix[0:1], matrix[1:2])
                similarity_score = float(sim[0][0]) * 100.0
            except Exception:
                similarity_score = 50.0

        # 3. Completeness & Length Heuristic
        words = len(answer_clean.split())
        length_score = 100.0 if words >= 30 else (words / 30.0) * 100.0

        # Unified Answer Score Formula
        # 50% Keyword Coverage + 30% Similarity + 20% Completeness
        final_score = (0.50 * keyword_score) + (0.30 * similarity_score) + (0.20 * length_score)
        final_score = max(0.0, min(100.0, final_score))

        # Feedback Generation
        strengths = []
        weaknesses = []
        suggestions = []

        if matched_keywords:
            strengths.append(f"Used relevant technical terms: {', '.join(matched_keywords[:4])}")
        if words >= 40:
            strengths.append("Provided a detailed explanation.")

        if missing_keywords:
            weaknesses.append(f"Missed key technical terms: {', '.join(missing_keywords[:4])}")
        if words < 25:
            weaknesses.append("Response could be more detailed.")

        if missing_keywords:
            suggestions.append(f"Consider discussing {missing_keywords[0]} in your response.")
        if final_score < 70:
            suggestions.append("Structure your answer using concrete examples and clear technical terminology.")

        relevance = 'Excellent' if final_score >= 80 else ('Good' if final_score >= 60 else 'Needs Improvement')

        feedback = {
            'relevance': relevance,
            'keyword_coverage': round(keyword_score, 1),
            'similarity_score': round(similarity_score, 1),
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
            'disclaimer': 'AI-generated scores are decision-support recommendations and should not replace human evaluation.'
        }

        return round(final_score, 1), feedback

    @classmethod
    def evaluate_interview_session(cls, questions_and_answers):
        """
        Evaluates a complete interview session.
        Calculates average score, overall strengths, weaknesses, and recommendations.
        """
        if not questions_and_answers:
            return 0.0, [], [], []

        total_score = 0.0
        all_strengths = []
        all_weaknesses = []
        all_suggestions = []

        for item in questions_and_answers:
            score = item.get('score', 0.0)
            fb = item.get('feedback', {})
            total_score += score

            if fb.get('strengths'):
                all_strengths.extend(fb['strengths'])
            if fb.get('weaknesses'):
                all_weaknesses.extend(fb['weaknesses'])
            if fb.get('suggestions'):
                all_suggestions.extend(fb['suggestions'])

        avg_score = total_score / len(questions_and_answers)

        # Deduplicate feedback lists
        unique_strengths = list(dict.fromkeys(all_strengths))[:4]
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:4]
        unique_suggestions = list(dict.fromkeys(all_suggestions))[:4]

        return round(avg_score, 1), unique_strengths, unique_weaknesses, unique_suggestions
