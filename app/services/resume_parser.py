import re
import os
import pypdf
from app.services.skill_extractor import extract_skills_from_text

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_path):
        """
        Extracts raw text from PDF using pypdf, with pdfplumber fallback.
        Handles empty, corrupted, or unreadable files gracefully.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("Resume PDF file not found.")

        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            if len(reader.pages) == 0:
                raise ValueError("Uploaded PDF document has no pages.")
                
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as primary_error:
            # Try pdfplumber as fallback
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception:
                raise ValueError(f"Could not parse PDF text: {str(primary_error)}")

        if not text.strip():
            raise ValueError("Uploaded PDF contains no extractable text (it might be scanned image-only PDF).")

        return text.strip()

    @staticmethod
    def parse_email(text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    @staticmethod
    def parse_phone(text):
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        matches = re.findall(phone_pattern, text)
        if matches:
            # Extract whole string match
            raw_match = re.search(phone_pattern, text)
            if raw_match:
                return raw_match.group(0).strip()
        return None

    @staticmethod
    def parse_name(text, email=None):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "Candidate"

        # Heuristic: First non-header line that isn't email/phone
        for line in lines[:5]:
            if "@" in line or re.search(r'\d{5,}', line):
                continue
            if len(line.split()) <= 4 and re.match(r'^[A-Za-z\s.\'-]+$', line):
                return line.title()

        if email:
            name_part = email.split('@')[0]
            name_part = re.sub(r'[^a-zA-Z]', ' ', name_part).strip()
            if name_part:
                return name_part.title()

        return "Candidate"

    @staticmethod
    def parse_education(text):
        education_keywords = [
            'B.Tech', 'B.E.', 'B.S.', 'B.Sc', 'M.Tech', 'M.E.', 'M.S.', 'M.Sc', 
            'Ph.D', 'Bachelor', 'Master', 'Doctorate', 'Diploma', 'Computer Science',
            'Engineering', 'Information Technology', 'Degree', 'University', 'College'
        ]
        text_lower = text.lower()
        found_education = []
        
        lines = text.split('\n')
        for line in lines:
            line_str = line.strip()
            if any(edu.lower() in line_str.lower() for edu in education_keywords):
                if len(line_str) < 120 and line_str not in found_education:
                    found_education.append(line_str)
                    
        return found_education[:5]

    @staticmethod
    def parse_experience_years(text):
        """
        Estimates total years of experience from text heuristics or date range matches.
        """
        # Look for explicit statements like "3 years of experience"
        exp_pattern = r'(\d+|\b(one|two|three|four|five|six|seven|eight|nine|ten)\b)\+?\s*years?(?:\s+of)?\s+experience'
        match = re.search(exp_pattern, text, re.IGNORECASE)
        if match:
            num_str = match.group(1).lower()
            word_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
            if num_str in word_map:
                return float(word_map[num_str])
            try:
                return float(num_str)
            except ValueError:
                pass

        # Look for date ranges e.g. 2020 - 2024
        year_matches = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
        if len(year_matches) >= 2:
            years = [int(y) for y in year_matches]
            years.sort()
            span = years[-1] - years[0]
            if 0 <= span <= 40:
                return float(span)

        return 1.0  # Default baseline for entry/mid candidate if unspecified

    @staticmethod
    def parse_projects(text):
        projects = []
        lines = text.split('\n')
        in_project_section = False
        
        for line in lines:
            line_str = line.strip()
            if re.search(r'\b(projects|key projects|portfolio)\b', line_str, re.IGNORECASE):
                in_project_section = True
                continue
            elif in_project_section and re.search(r'\b(education|experience|skills|certifications)\b', line_str, re.IGNORECASE):
                in_project_section = False
                
            if in_project_section and line_str:
                if len(line_str) > 10 and len(projects) < 5:
                    projects.append(line_str)

        return projects

    @staticmethod
    def parse_certifications(text):
        certs = []
        cert_keywords = ['certified', 'certification', 'certificate', 'aws certified', 'coursera', 'udemy', 'nptel', 'oracle']
        for line in text.split('\n'):
            line_str = line.strip()
            if any(ck in line_str.lower() for ck in cert_keywords):
                if len(line_str) < 100 and line_str not in certs:
                    certs.append(line_str)
        return certs[:5]

    @classmethod
    def parse(cls, file_path):
        raw_text = cls.extract_text_from_pdf(file_path)
        email = cls.parse_email(raw_text)
        phone = cls.parse_phone(raw_text)
        name = cls.parse_name(raw_text, email)
        education = cls.parse_education(raw_text)
        exp_years = cls.parse_experience_years(raw_text)
        projects = cls.parse_projects(raw_text)
        certifications = cls.parse_certifications(raw_text)
        skills = extract_skills_from_text(raw_text)

        return {
            'raw_text': raw_text,
            'name': name,
            'email': email,
            'phone': phone,
            'education': education,
            'experience_years': exp_years,
            'projects': projects,
            'certifications': certifications,
            'skills': skills
        }
