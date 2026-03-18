from backend.schemas import JobData, Profile


def generate_evaluation_prompt(profile: Profile, job: JobData) -> str:

    profile_text = f"""Name: {profile.name}
    Title: {profile.title}
    Experience: {profile.experience}
    Skills: {', '.join(profile.skills)}
    Education: {profile.education}
    Location: {profile.location}
    Summary: {profile.summary}"""
    
    prompt = f"""You are evaluating a job listing for a candidate. Score the match from 0-100 and give a 1-2 sentence summary of why.

    CANDIDATE PROFILE:
    {profile_text}

    JOB LISTING:
    Title: {job.title}
    Company: {job.company or 'Unknown'}
    Location: {job.location or 'Not specified'}
    Description: {(job.description or 'No description available')[:800]}

    For matched_skills: List skills from the candidate profile that are mentioned in or relevant to the job description.
    For missing_skills: List skills required by the job that the candidate does NOT have.

    IMPORTANT: Normalize skill names when matching. Treat these as the SAME skill:
    - React, ReactJS, React.js
    - Python, Python3, Py
    - TypeScript, TS
    - JavaScript, JS
    - Node.js, Node, NodeJS
    - Angular.js, Angular
    - Vue.js, Vue
    - C#, CSharp, C Sharp, Csharp
    - C++, Cpp, C plus plus
    - Azure, Microsoft Azure, Azure Cloud
    - AWS, Amazon Web Services
    - GCP, Google Cloud
    - Docker, Containerization
    - Kubernetes, K8s
    - PostgreSQL, Postgres, PG
    - MySQL, MySQL Database
    - MongoDB, Mongo, NoSQL
    - LLM, Large Language Model, AI, Artificial Intelligence, Machine Learning, ML, Deep Learning
    - REST, RESTful API, REST API
    - GraphQL, Graph QL
    - Django, Django REST Framework, DRF
    - FastAPI, Fast API
    - Express, Express.js, ExpressJS
    - Git, GitHub, Version Control
    - Docker, Containerization, Container, Containers
    - Etc. - Be flexible and match similar technologies and frameworks.

    Respond ONLY with valid JSON in this exact format:
    {{"score": 75, "summary": "Strong match because...", "matched_skills": ["skill1", "skill2", ...], "missing_skills": ["skill3", "skill4", ...]}}"""

    return prompt



CV_VISION_PROMPT = """Analyze this CV/Resume image and extract a structured profile. Extract all information visible in the document.

For skills: Extract ONLY the skills, technologies, languages, tools, and frameworks explicitly shown in the CV image. Do NOT infer or assume skills - only include what is directly visible or stated.

Respond ONLY with valid JSON in this exact format:
{
  "name": "Full Name",
  "title": "Current/Target Job Title (e.g. Full-Stack Developer)",
  "experience": "X years of experience in Y (be specific about total years)",
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5", ...],
  "education": "Highest degree and field",
  "location": "City, Country",
  "summary": "2-3 sentence professional summary highlighting key strengths"
}"""


CV_ANALYSIS_PROMPT = """Analyze this CV/Resume and extract a structured profile.

CV TEXT:
{cv_text}

For skills: Extract ONLY the skills, technologies, languages, tools, and frameworks explicitly mentioned in the CV text. Do NOT infer or assume skills - only include what is directly stated.

Respond ONLY with valid JSON in this exact format:
{{
  "name": "Full Name",
  "title": "Current/Target Job Title (e.g. Full-Stack Developer)",
  "experience": "X years of experience in Y",
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5", ...],
  "education": "Highest degree and field",
  "location": "City, Country",
  "summary": "2-3 sentence professional summary highlighting key strengths"
}}"""