import re

# Centralized Skill Database & Taxonomy
SKILL_TAXONOMY = {
    'Programming': [
        'Python', 'Java', 'C', 'C++', 'C#', 'JavaScript', 'TypeScript', 'Go', 
        'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'R', 'Scala'
    ],
    'AI/ML': [
        'Machine Learning', 'Deep Learning', 'Natural Language Processing', 'NLP',
        'Computer Vision', 'Neural Networks', 'Reinforcement Learning', 'Large Language Models',
        'LLM', 'Transformers', 'GenAI', 'Generative AI', 'Feature Engineering', 'Model Deployment'
    ],
    'Web': [
        'Flask', 'Django', 'FastAPI', 'React', 'React.js', 'Vue.js', 'Angular',
        'Node.js', 'Express.js', 'HTML5', 'CSS3', 'Bootstrap', 'Tailwind CSS', 'REST API', 'GraphQL'
    ],
    'Database': [
        'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis', 'Cassandra', 'Elasticsearch',
        'Oracle', 'SQL Server', 'DynamoDB', 'Database Design', 'SQL'
    ],
    'Cloud/DevOps': [
        'AWS', 'Amazon Web Services', 'Azure', 'GCP', 'Google Cloud Platform',
        'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Terraform', 'Git', 'GitHub', 'Linux', 'Bash'
    ],
    'Data': [
        'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Keras', 'OpenCV',
        'SciPy', 'Apache Spark', 'Hadoop', 'Data Analysis', 'Data Visualization', 'Tableau', 'PowerBI'
    ],
    'Soft Skills': [
        'Problem Solving', 'Team Leadership', 'Communication', 'Agile', 'Scrum', 'Critical Thinking'
    ]
}

# Skill aliases for normalization
SKILL_ALIASES = {
    'js': 'JavaScript',
    'ts': 'TypeScript',
    'py': 'Python',
    'postgres': 'PostgreSQL',
    'postgres sql': 'PostgreSQL',
    'mongo': 'MongoDB',
    'ml': 'Machine Learning',
    'dl': 'Deep Learning',
    'nlp': 'Natural Language Processing',
    'cv': 'Computer Vision',
    'reactjs': 'React',
    'nodejs': 'Node.js',
    'express': 'Express.js',
    'sklearn': 'Scikit-learn',
    'tf': 'TensorFlow',
    'aws': 'AWS',
    'gcp': 'GCP',
    'k8s': 'Kubernetes'
}

def get_all_skills_flat():
    """Return normalized skill name -> category metadata."""
    flat = {}
    for category, skills in SKILL_TAXONOMY.items():
        for name in skills:
            flat[name.lower()] = {'name': name, 'category': category}
    return flat


def canonicalize_skill(skill):
    """Normalize common aliases so matching is consistent across resumes and jobs."""
    value = (skill or '').strip()
    if not value:
        return ''
    alias = SKILL_ALIASES.get(value.lower())
    if alias:
        return alias
    metadata = get_all_skills_flat().get(value.lower())
    return metadata['name'] if metadata else value


def extract_skills_from_text(text):
    """Extract standardized skills from resume/job text using safe regex boundaries."""
    if not text:
        return []

    matched_skills = {}

    # Check aliases first.
    for alias, canonical in SKILL_ALIASES.items():
        if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', text, re.IGNORECASE):
            category = next(
                (cat for cat, names in SKILL_TAXONOMY.items() if canonical in names),
                'Other'
            )
            matched_skills[canonical] = category

    # Taxonomy check. Special characters such as + and # need custom boundaries.
    for category, skill_list in SKILL_TAXONOMY.items():
        for name in skill_list:
            if name in matched_skills:
                continue
            if name == 'C++':
                pattern = r'(?<!\w)C\+\+(?!\w)'
            elif name == 'C#':
                pattern = r'(?<!\w)C#(?!\w)'
            elif name == 'C':
                pattern = r'(?<![A-Za-z0-9_])C(?![A-Za-z0-9_])'
            else:
                pattern = r'(?<!\w)' + re.escape(name) + r'(?!\w)'
            if re.search(pattern, text, re.IGNORECASE):
                matched_skills[name] = category

    return [{'name': name, 'category': category} for name, category in matched_skills.items()]
