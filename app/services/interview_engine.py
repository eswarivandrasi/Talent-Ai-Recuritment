import random

# Centralized Question Bank
QUESTION_BANK = [
    # Technical - Python
    {
        'skill': 'Python',
        'category': 'Technical',
        'difficulty': 'Easy',
        'question': 'Explain the difference between lists and tuples in Python. When would you use each?',
        'keywords': ['mutable', 'immutable', 'memory', 'performance', 'parentheses', 'brackets'],
        'sample_answer': 'Lists are mutable and defined with square brackets, allowing modifications after creation. Tuples are immutable and defined with parentheses, making them more memory efficient and suitable for fixed data.'
    },
    {
        'skill': 'Python',
        'category': 'Technical',
        'difficulty': 'Medium',
        'question': 'How do Python decorators work? Can you give a practical use case for a decorator?',
        'keywords': ['wrapper', 'higher-order function', 'functools', 'wraps', 'logging', 'authentication', 'arguments'],
        'sample_answer': 'Decorators take a function as an argument, wrap its execution with additional behavior (like logging or timing), and return the wrapped function without modifying the original source code.'
    },
    {
        'skill': 'Python',
        'category': 'Technical',
        'difficulty': 'Hard',
        'question': 'Describe Python GIL (Global Interpreter Lock) and how it affects multi-threading vs multi-processing.',
        'keywords': ['GIL', 'thread', 'bytecode', 'CPU-bound', 'I/O-bound', 'multiprocessing', 'concurrency'],
        'sample_answer': 'The GIL ensures only one thread executes Python bytecode at a time. It limits CPU-bound multi-threading performance, making multiprocessing necessary for true parallel CPU execution.'
    },

    # Technical - Machine Learning / AI
    {
        'skill': 'Machine Learning',
        'category': 'Technical',
        'difficulty': 'Easy',
        'question': 'What is the difference between supervised and unsupervised machine learning?',
        'keywords': ['labeled', 'unlabeled', 'regression', 'classification', 'clustering', 'target variable'],
        'sample_answer': 'Supervised learning trains on labeled data to predict target outcomes, whereas unsupervised learning finds hidden patterns and structures in unlabeled data (e.g., clustering).'
    },
    {
        'skill': 'Machine Learning',
        'category': 'Technical',
        'difficulty': 'Medium',
        'question': 'Explain overfitting and underfitting. What techniques do you use to prevent overfitting?',
        'keywords': ['variance', 'bias', 'regularization', 'cross-validation', 'dropout', 'data augmentation', 'early stopping'],
        'sample_answer': 'Overfitting occurs when a model learns noise in training data (high variance). It can be mitigated using regularization (L1/L2), cross-validation, dropout, and early stopping.'
    },
    {
        'skill': 'Machine Learning',
        'category': 'Technical',
        'difficulty': 'Hard',
        'question': 'How does precision-recall tradeoff work? When would you optimize for Precision over Recall?',
        'keywords': ['false positive', 'false negative', 'threshold', 'F1-score', 'spam detection', 'medical diagnosis'],
        'sample_answer': 'Precision measures accuracy of positive predictions, while recall measures coverage of actual positives. Precision is optimized when false positives are costly (e.g., spam detection).'
    },

    # Technical - SQL / Database
    {
        'skill': 'SQL',
        'category': 'Technical',
        'difficulty': 'Easy',
        'question': 'What is the difference between WHERE and HAVING clauses in SQL?',
        'keywords': ['aggregate', 'GROUP BY', 'filter', 'rows', 'groups'],
        'sample_answer': 'WHERE filters rows before aggregation, whereas HAVING filters aggregated groups after the GROUP BY clause is processed.'
    },
    {
        'skill': 'SQL',
        'category': 'Technical',
        'difficulty': 'Medium',
        'question': 'Explain SQL indexes. How do they improve query performance and what is their downside?',
        'keywords': ['B-tree', 'lookup', 'write performance', 'INSERT', 'UPDATE', 'storage', 'full table scan'],
        'sample_answer': 'Indexes speed up search queries by creating lookup structures (e.g., B-trees), but slow down write operations (INSERT/UPDATE) due to index maintenance overhead.'
    },

    # Technical - Web / Flask / React
    {
        'skill': 'Flask',
        'category': 'Technical',
        'difficulty': 'Medium',
        'question': 'How do you handle authentication and database sessions in a Flask application?',
        'keywords': ['SQLAlchemy', 'session', 'cookies', 'JWT', 'Werkzeug', 'hash', 'security'],
        'sample_answer': 'Flask uses secure signed cookies for session management and SQLAlchemy scoped sessions for database operations, storing hashed passwords via Werkzeug.'
    },
    {
        'skill': 'React',
        'category': 'Technical',
        'difficulty': 'Medium',
        'question': 'Explain the Virtual DOM in React and how reconciliation works.',
        'keywords': ['virtual DOM', 'diffing algorithm', 'reconciliation', 'render', 'DOM update', 'performance'],
        'sample_answer': 'React uses an in-memory Virtual DOM to calculate UI diffs during state changes and efficiently updates only changed real DOM nodes.'
    },

    # Behavioral
    {
        'skill': 'General',
        'category': 'Behavioral',
        'difficulty': 'Medium',
        'question': 'Describe a situation where you faced a tight deadline or technical obstacle. How did you handle it?',
        'keywords': ['prioritization', 'communication', 'problem-solving', 'teamwork', 'deadline', 'solution'],
        'sample_answer': 'Focus on using the STAR method: Situation, Task, Action taken, and Result achieved, highlighting effective prioritization and communication.'
    },

    # HR
    {
        'skill': 'General',
        'category': 'HR',
        'difficulty': 'Easy',
        'question': 'Why are you interested in this role and what makes you a good fit for our team?',
        'keywords': ['motivation', 'skills', 'culture fit', 'growth', 'impact', 'company values'],
        'sample_answer': 'Demonstrate alignment between your technical expertise, career goals, and the company mission.'
    },

    # Project-based
    {
        'skill': 'General',
        'category': 'Project-based',
        'difficulty': 'Medium',
        'question': 'Walk us through your most challenging AI or software project. What technical decisions did you make?',
        'keywords': ['architecture', 'tradeoffs', 'tech stack', 'scaling', 'lessons learned', 'results'],
        'sample_answer': 'Outline project objectives, chosen technologies, architecture tradeoffs, key challenges overcome, and measurable outcomes.'
    }
]

class InterviewEngine:
    @staticmethod
    def generate_questions(job_skills, candidate_skills, question_count=5, difficulty='Medium'):
        """
        Generates a tailored question set combining technical skill questions,
        project questions, and HR/Behavioral questions.
        """
        all_skills = set([s.strip() for s in job_skills] + [s.strip() for s in candidate_skills])
        selected_questions = []

        # 1. Select technical questions matching skills & difficulty
        technical_matches = [
            q for q in QUESTION_BANK 
            if q['category'] == 'Technical' and (
                any(s.lower() == q['skill'].lower() for s in all_skills) or q['difficulty'] == difficulty
            )
        ]
        
        random.shuffle(technical_matches)
        
        # Pick 60% technical
        tech_target = max(1, int(question_count * 0.6))
        selected_questions.extend(technical_matches[:tech_target])

        # 2. Select Project-based question
        project_qs = [q for q in QUESTION_BANK if q['category'] == 'Project-based']
        if project_qs:
            selected_questions.append(random.choice(project_qs))

        # 3. Select HR / Behavioral questions to reach question_count
        other_qs = [q for q in QUESTION_BANK if q['category'] in ['HR', 'Behavioral']]
        random.shuffle(other_qs)
        
        while len(selected_questions) < question_count and other_qs:
            selected_questions.append(other_qs.pop(0))

        # If still short, fill from remaining general questions
        if len(selected_questions) < question_count:
            remaining = [q for q in QUESTION_BANK if q not in selected_questions]
            random.shuffle(remaining)
            selected_questions.extend(remaining[:question_count - len(selected_questions)])

        return selected_questions[:question_count]
