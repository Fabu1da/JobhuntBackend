from backend.schemas import JobData, Profile


def evaluation_jobs(profile: Profile, jobs: list[JobData]) -> str:

    profile_text = f"""Name: {profile.name}
    Title: {profile.title}
    Experience: {profile.experience}
    Skills: {', '.join(profile.skills)}
    Education: {profile.education}
    Location: {profile.location}
    Summary: {profile.summary}"""

    jobs_text = "\n\n".join([
        f"JOB {i+1} (ID: {job.id}):\nTitle: {job.title}\nCompany: {job.company or 'Unknown'}\nLocation: {job.location or 'Not specified'}\nDescription: {(job.description or 'No description')[:400]}"
        for i, job in enumerate(jobs)
    ])

    prompt = f"""You are evaluating multiple job listings for a candidate. For EACH job, score the match from 0-100 and give a brief summary.

    CANDIDATE PROFILE:
    {profile_text}

    JOB LISTINGS:
    {jobs_text}

    For each job:
    - matched_skills: List skills from the candidate profile that are mentioned in or relevant to the job description.
    - missing_skills: List skills required by the job that the candidate does NOT have.

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



    Analyze the following job description and include in your evaluation:

    Verdict — Strong match / Decent match / Borderline / Skip — in one sentence
    action — Apply / Consider / Postpone / Ignore — in one sentence

    Strong matches — skills and experience that directly align
    Gaps — missing skills or experience, noting if critical or minor
    Hard blockers — anything that makes applying pointless (German required, wrong stack, wrong level)
    Stand out — unique advantages for this specific role
    Salary target — suggested range based on role and company type
    Recommendation — apply, skip, or apply later with reasoning

    Respond ONLY with a valid JSON array containing one object per job in this exact format:
    [{{"id": "job_id", "score": 75, "summary": "Strong match because...", "Verdict": "Strong match", "action": "Apply", "matched_skills": "["skill1", "skill2", ...]", "missing_skills": "["skill3", "skill4", ...]", "Gaps": "Missing skills...",  "Hard blockers": "Requirements not met...", "Stand out": "Unique qualifications...", "Salary target": "X - Y", "Recommendation": "Apply, skip, or apply later with reasoning"}}, ...]

    IMPORTANT: Return scores for ALL jobs in the same order. Use the exact job IDs provided. Make sure matched_skills and missing_skills are JSON arrays, not strings."""

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