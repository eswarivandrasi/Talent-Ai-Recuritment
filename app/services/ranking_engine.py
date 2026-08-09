class RankingEngine:
    DEFAULT_WEIGHTS = {
        'resume_match': 0.40,
        'interview': 0.35,
        'skill_match': 0.15,
        'experience': 0.10
    }

    @classmethod
    def calculate_experience_score(cls, candidate_years, required_years):
        """
        Calculates experience score out of 100 based on candidate years vs required years.
        """
        if required_years <= 0:
            return 100.0
        
        ratio = (candidate_years / float(required_years)) * 100.0
        return max(0.0, min(100.0, ratio))

    @classmethod
    def calculate_final_score(cls, resume_match, interview_score, skill_match, experience_score, weights=None):
        """
        Calculates final composite score using dynamic configurable weights.
        Returns final_score (0-100) and detailed breakdown dict.
        """
        w = dict(cls.DEFAULT_WEIGHTS)
        if weights:
            for key in w:
                try:
                    value = float(weights.get(key, w[key]))
                except (TypeError, ValueError):
                    value = w[key]
                w[key] = max(0.0, value)

        # Normalize weights to ensure sum = 1.0
        total_w = sum(w.values())
        if total_w > 0:
            norm_w = {k: v / total_w for k, v in w.items()}
        else:
            norm_w = cls.DEFAULT_WEIGHTS

        f_resume = resume_match * norm_w.get('resume_match', 0.40)
        f_interview = interview_score * norm_w.get('interview', 0.35)
        f_skill = skill_match * norm_w.get('skill_match', 0.15)
        f_exp = experience_score * norm_w.get('experience', 0.10)

        final_score = f_resume + f_interview + f_skill + f_exp
        final_score = max(0.0, min(100.0, final_score))

        breakdown = {
            'resume_match_contrib': round(f_resume, 1),
            'interview_contrib': round(f_interview, 1),
            'skill_match_contrib': round(f_skill, 1),
            'experience_contrib': round(f_exp, 1),
            'weights_used': {k: round(v * 100, 1) for k, v in norm_w.items()}
        }

        return round(final_score, 1), breakdown

    @classmethod
    def generate_skill_gap_analysis(cls, job_title, matching_skills, missing_skills):
        """
        Generates structured Skill Gap Analysis with recommendations.
        """
        recommendations = []
        for idx, skill in enumerate(missing_skills[:5], 1):
            recommendations.append(f"{idx}. Master {skill} fundamentals and complete a practical hands-on project.")

        if not recommendations:
            recommendations.append("You meet all core skill requirements for this position!")

        summary = f"Match score for {job_title} is based on skill overlap and candidate qualifications."

        return {
            'strong_skills': matching_skills,
            'missing_skills': missing_skills,
            'learning_recommendations': recommendations,
            'summary': summary
        }
