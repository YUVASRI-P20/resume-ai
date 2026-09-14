"""
Canonical seed data for companies / job roles / requirements.

Used by:
- alembic migration 0005 (Postgres deployments), and
- the sqlite dev bootstrap (app.database.bootstrap.seed_sqlite).

This is the ONLY place job seed data is defined — extend this list to add
companies or roles; no code changes needed elsewhere.
"""

SEED_DATA = [
    {
        "company": "Google",
        "industry": "Technology",
        "description": "Products and services across search, cloud, ads and AI.",
        "roles": [
            {
                "title": "Software Engineer",
                "domain": "Software Engineering",
                "seniority": "Mid",
                "description": "Build and ship software systems across Google's product surface.",
                "requirements": [
                    ("Python", "skill", 5), ("Data Structures", "concept", 5), ("Algorithms", "concept", 5),
                    ("System Design", "concept", 4), ("SQL", "skill", 3), ("Distributed Systems", "concept", 3),
                    ("Linux", "tool", 2), ("Git", "tool", 3),
                ],
            },
            {
                "title": "Machine Learning Engineer",
                "domain": "AI/ML",
                "seniority": "Mid",
                "description": "Train, evaluate and deploy ML models into production systems.",
                "requirements": [
                    ("Python", "skill", 5), ("Machine Learning", "concept", 5), ("PyTorch", "technology", 4),
                    ("TensorFlow", "technology", 3), ("SQL", "skill", 4), ("Statistics", "concept", 4),
                    ("AWS", "technology", 3), ("Docker", "technology", 3),
                ],
            },
        ],
    },
    {
        "company": "Microsoft",
        "industry": "Technology",
        "description": "Software, cloud (Azure) and productivity platforms.",
        "roles": [
            {
                "title": "Software Engineer",
                "domain": "Software Engineering",
                "seniority": "Mid",
                "description": "Engineer cloud-scale services and developer tools.",
                "requirements": [
                    ("C#", "skill", 4), ("Python", "skill", 4), ("Azure", "technology", 4),
                    ("REST APIs", "concept", 4), ("SQL", "skill", 3), ("System Design", "concept", 4),
                    ("Docker", "technology", 3), ("CI/CD", "concept", 3),
                ],
            },
        ],
    },
    {
        "company": "Amazon",
        "industry": "E-commerce / Cloud",
        "description": "Global e-commerce and AWS cloud services.",
        "roles": [
            {
                "title": "Software Development Engineer",
                "domain": "Software Engineering",
                "seniority": "Mid",
                "description": "Design and build scalable services on AWS infrastructure.",
                "requirements": [
                    ("Java", "skill", 4), ("Python", "skill", 4), ("AWS", "technology", 5),
                    ("System Design", "concept", 5), ("SQL", "skill", 4), ("Docker", "technology", 3),
                    ("Kubernetes", "technology", 3), ("Microservices", "concept", 4),
                ],
            },
            {
                "title": "Backend Engineer",
                "domain": "Backend",
                "seniority": "Mid",
                "description": "Build high-throughput backend services and APIs.",
                "requirements": [
                    ("Python", "skill", 5), ("Java", "skill", 3), ("AWS", "technology", 4),
                    ("REST APIs", "concept", 5), ("PostgreSQL", "technology", 4), ("Redis", "technology", 3),
                    ("Microservices", "concept", 4), ("Docker", "technology", 3),
                ],
            },
        ],
    },
    {
        "company": "Zoho",
        "industry": "SaaS",
        "description": "Business software suite (CRM, finance, collaboration).",
        "roles": [
            {
                "title": "Software Developer",
                "domain": "Fullstack",
                "seniority": "Entry",
                "description": "Full-stack product development across Zoho's business apps.",
                "requirements": [
                    ("Java", "skill", 5), ("JavaScript", "skill", 4), ("SQL", "skill", 5),
                    ("Data Structures", "concept", 4), ("Algorithms", "concept", 4),
                    ("REST APIs", "concept", 3), ("HTML5", "skill", 2), ("CSS3", "skill", 2),
                ],
            },
        ],
    },
    {
        "company": "TCS",
        "industry": "IT Services",
        "description": "Global IT services and consulting.",
        "roles": [
            {
                "title": "Systems Engineer",
                "domain": "Software Engineering",
                "seniority": "Entry",
                "description": "Application development, support and maintenance across client projects.",
                "requirements": [
                    ("Python", "skill", 4), ("Java", "skill", 4), ("SQL", "skill", 4),
                    ("Data Structures", "concept", 3), ("Git", "tool", 3), ("REST APIs", "concept", 3),
                    ("Linux", "tool", 2),
                ],
            },
        ],
    },
    {
        "company": "Infosys",
        "industry": "IT Services",
        "description": "Digital services and consulting.",
        "roles": [
            {
                "title": "Software Engineer",
                "domain": "Software Engineering",
                "seniority": "Entry",
                "description": "Build and maintain enterprise applications for global clients.",
                "requirements": [
                    ("Java", "skill", 4), ("Python", "skill", 3), ("SQL", "skill", 4),
                    ("Spring Boot", "technology", 3), ("REST APIs", "concept", 3), ("Git", "tool", 3),
                    ("Data Structures", "concept", 3),
                ],
            },
        ],
    },
    {
        "company": "Accenture",
        "industry": "Consulting",
        "description": "Technology consulting and digital transformation.",
        "roles": [
            {
                "title": "Application Developer",
                "domain": "Fullstack",
                "seniority": "Entry",
                "description": "Develop and deliver application features for enterprise clients.",
                "requirements": [
                    ("JavaScript", "skill", 4), ("Python", "skill", 3), ("SQL", "skill", 4),
                    ("React", "technology", 3), ("Node.js", "technology", 3), ("REST APIs", "concept", 3),
                    ("Git", "tool", 3), ("CI/CD", "concept", 2),
                ],
            },
        ],
    },
    {
        "company": "Flipkart",
        "industry": "E-commerce",
        "description": "India's leading e-commerce marketplace.",
        "roles": [
            {
                "title": "Software Engineer II",
                "domain": "Backend",
                "seniority": "Mid",
                "description": "Scale marketplace services for hundreds of millions of users.",
                "requirements": [
                    ("Java", "skill", 5), ("Python", "skill", 3), ("Microservices", "concept", 5),
                    ("Kafka", "technology", 4), ("SQL", "skill", 4), ("Redis", "technology", 3),
                    ("System Design", "concept", 4), ("AWS", "technology", 3),
                ],
            },
        ],
    },
    {
        "company": "Adobe",
        "industry": "Software",
        "description": "Creative, document and experience cloud software.",
        "roles": [
            {
                "title": "Software Engineer",
                "domain": "Software Engineering",
                "seniority": "Mid",
                "description": "Build features across Adobe's creative and cloud products.",
                "requirements": [
                    ("Java", "skill", 4), ("C++", "skill", 3), ("Python", "skill", 3),
                    ("Data Structures", "concept", 5), ("Algorithms", "concept", 5),
                    ("REST APIs", "concept", 3), ("Docker", "technology", 2), ("SQL", "skill", 3),
                ],
            },
        ],
    },
    {
        "company": "Oracle",
        "industry": "Software / Cloud",
        "description": "Database, middleware and cloud infrastructure.",
        "roles": [
            {
                "title": "Software Engineer",
                "domain": "Backend",
                "seniority": "Mid",
                "description": "Develop database and cloud infrastructure software.",
                "requirements": [
                    ("Java", "skill", 5), ("SQL", "skill", 5), ("Python", "skill", 3),
                    ("Data Structures", "concept", 4), ("Linux", "tool", 3), ("Docker", "technology", 2),
                    ("REST APIs", "concept", 3),
                ],
            },
        ],
    },
]


def build_seed_rows() -> list[dict]:
    return SEED_DATA
