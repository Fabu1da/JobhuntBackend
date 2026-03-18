from pydantic import BaseModel
from typing import List, Optional


class Profile(BaseModel):
    name: str
    title: str
    experience: str
    skills: List[str]
    education: str
    location: str
    summary: str


class JobData(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ScoreRequest(BaseModel):
    profile: Profile
    job: JobData


class BatchScoreRequest(BaseModel):
    profile: Profile
    jobs: List[JobData]


class AnalyzeCvRequest(BaseModel):
    cv_text: str
    pdf_images: Optional[List[str]] = None  # Base64 encoded PNG images of PDF pages
