"""
skills_db.py
------------
A curated keyword database used for lightweight, offline skill extraction.
No internet / external NLP model download is required.

You can freely extend SKILLS_DB with more categories/skills to fit your
domain (e.g., add "Marketing", "Finance", "Design" categories).
"""

SKILLS_DB = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go", "golang",
        "rust", "r", "matlab", "scala", "kotlin", "swift", "php", "ruby", "sql",
        "c", "perl", "dart", "shell scripting", "bash"
    ],
    "Web Development": [
        "html", "css", "react", "reactjs", "angular", "vue", "vuejs", "node.js",
        "nodejs", "express.js", "django", "flask", "fastapi", "spring boot",
        "next.js", "nuxt.js", "bootstrap", "tailwind css", "jquery", "rest api",
        "graphql", "webpack", "redux"
    ],
    "Data Science & ML": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "data science", "data analysis", "data visualization",
        "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch",
        "keras", "opencv", "xgboost", "statistics", "regression", "classification",
        "clustering", "neural networks", "llm", "generative ai", "feature engineering",
        "matplotlib", "seaborn", "power bi", "tableau"
    ],
    "Databases": [
        "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
        "cassandra", "dynamodb", "firebase", "elasticsearch", "mariadb",
        "microsoft sql server", "nosql"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins",
        "ci/cd", "terraform", "ansible", "linux", "git", "github", "gitlab",
        "devops", "microservices", "cloud computing", "lambda", "ec2", "s3"
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "time management", "project management", "agile",
        "scrum", "adaptability", "collaboration", "presentation", "negotiation"
    ],
    "Tools & Other": [
        "excel", "jira", "confluence", "figma", "postman", "vs code",
        "android studio", "unity", "selenium", "pytest", "junit", "api testing",
        "etl", "big data", "hadoop", "spark", "kafka", "airflow"
    ],
}

# Flat lookup set for fast membership checks (all lowercase)
ALL_SKILLS = sorted({skill.lower() for group in SKILLS_DB.values() for skill in group})

DEGREE_KEYWORDS = [
    "b.tech", "btech", "bachelor of technology", "b.e", "be ", "bachelor of engineering",
    "m.tech", "mtech", "master of technology", "bsc", "b.sc", "msc", "m.sc",
    "mba", "bca", "mca", "phd", "ph.d", "diploma", "bachelor", "master",
]
