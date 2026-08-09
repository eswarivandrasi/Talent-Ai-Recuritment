import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.skill_extractor import canonicalize_skill

class JobMatcher:
    @staticmethod
    def preprocess_text(text):
        if not text:
            return ""
        # Lowercase and clean special characters except relevant symbols
        clean = re.sub(r'[^a-zA-Z0-9\s+#.]', ' ', text.lower())
        # Strip extra whitespace
        return ' '.join(clean.split())

    @classmethod
    def calculate_text_similarity(cls, resume_text, job_text):
        """
        Computes Cosine Similarity between resume text and job description using TF-IDF.
        Returns a score between 0.0 and 100.0.
        """
        clean_resume = cls.preprocess_text(resume_text)
        clean_job = cls.preprocess_text(job_text)

        if not clean_resume or not clean_job:
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )
            tfidf_matrix = vectorizer.fit_transform([clean_job, clean_resume])
            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = float(sim_matrix[0][0]) * 100.0
            return max(0.0, min(100.0, similarity_score))
        except Exception:
            return 0.0

    @classmethod
    def calculate_skill_overlap(cls, candidate_skills_list, required_skills_list):
        """
        Calculates skill match ratio and identifies matching vs missing skills.
        """
        if not required_skills_list:
            return 100.0, list(candidate_skills_list), []

        candidate_normalized = [canonicalize_skill(s) for s in candidate_skills_list if str(s).strip()]
        required_normalized = [canonicalize_skill(s) for s in required_skills_list if str(s).strip()]

        cand_map = {s.lower(): s for s in candidate_normalized if s}
        req_map = {s.lower(): s for s in required_normalized if s}
        cand_set = set(cand_map)
        req_set = set(req_map)

        if not req_set:
            return 100.0, list(cand_map.values()), []

        matching_lower = cand_set.intersection(req_set)
        missing_lower = req_set - cand_set

        matching_skills = [req_map[s] for s in sorted(matching_lower)]
        missing_skills = [req_map[s] for s in sorted(missing_lower)]

        skill_match_ratio = (len(matching_lower) / len(req_set)) * 100.0
        return max(0.0, min(100.0, skill_match_ratio)), matching_skills, missing_skills

    @classmethod
    def match(cls, resume_text, candidate_skills, job_description, required_skills):
        """
        Complete Resume-Job Matcher Pipeline.
        Calculates TF-IDF Similarity, Skill Match Score, Matching Skills, Missing Skills,
        and unified Match Score.
        """
        # Calculate TF-IDF Text Similarity
        text_similarity = cls.calculate_text_similarity(resume_text, job_description)
        
        # Calculate Skill Match Score
        skill_score, matching_skills, missing_skills = cls.calculate_skill_overlap(
            candidate_skills, required_skills
        )

        # Transparent Unified Score: 50% Text Cosine Similarity + 50% Skill Match Score
        overall_match_score = (0.50 * text_similarity) + (0.50 * skill_score)
        
        # Boost slightly if skills match heavily even if text layout is different
        if skill_score >= 80.0 and overall_match_score < 75.0:
            overall_match_score = (0.30 * text_similarity) + (0.70 * skill_score)

        return {
            'overall_match_score': round(overall_match_score, 1),
            'text_similarity_score': round(text_similarity, 1),
            'skill_match_score': round(skill_score, 1),
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }
