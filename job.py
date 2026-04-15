from sqlmodel import Session, select
from .models.job import Job




async def saveJob(session: Session, job_data: dict) -> Job:
    """Create a new job entry in the database."""

    print(job_data)

    # Convert skill lists to counts
    matched_skills = job_data.get("matched_skills")
    if isinstance(matched_skills, list):
        matched_skills = len(matched_skills)
    
    missing_skills = job_data.get("missing_skills")
    if isinstance(missing_skills, list):
        missing_skills = len(missing_skills)

    job = Job(
        user_id=job_data.get("user_id"),
        title=job_data.get("title"),
        company=job_data.get("company"),
        location=job_data.get("location"),
        description=job_data.get("description"),
        requirements=job_data.get("requirements") or "",
        posted_date=job_data.get("date_posted"),
        url=job_data.get("job_url"),
        action=job_data.get("Action"),
        score=job_data.get("score"),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        Verdict=job_data.get("Verdict"),
        Gaps=job_data.get("Gaps"),
        Hard_blockers=job_data.get("Hard_blockers"),
        stand_out=job_data.get("stand_out"),
        ai_summary=job_data.get("ai_summary"),
        gap=job_data.get("gap"),
        hard_blocker=job_data.get("hard_blocker"),
        stand_out_point=job_data.get("stand_out_point"),
        recommendation=job_data.get("Recommendation"),
        site=job_data.get("site"),
        Salary_target=job_data.get("Salary_target"),
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job



async def getAllJobs(session: Session) -> list[Job]:
    """Retrieve all job entries from the database."""
    jobs = select(Job)
    return session.exec(jobs).all()

async def deleteJob(session: Session, job_id: int) -> bool:
    """Delete a job entry from the database by its ID."""
    job = session.get(Job, job_id)
    if job:
        session.delete(job)
        session.commit()
        return True
    return False