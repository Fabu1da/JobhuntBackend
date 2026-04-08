
from typing import Annotated, Optional
from sqlmodel import SQLModel, Field



class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    posted_date: Optional[str] = None
    url: Optional[str] = None
    action: Optional[str] = None
    score: Optional[float] = None
    matched_skills: Optional[int] = None
    missing_skills: Optional[int] = None
    Verdict: Optional[str] = None
    Gaps: Optional[str] = None
    Hard_blockers: Optional[str] = None
    stand_out: Optional[str] = None
    ai_summary: Optional[str] = None
    gap: Optional[str] = None
    hard_blocker: Optional[str] = None
    stand_out_point: Optional[str] = None
    recommendation: Optional[str] = None
    site: Optional[str] = None
    Salary_target: Optional[str] = None
    
