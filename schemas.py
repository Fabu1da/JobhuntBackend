from pydantic import BaseModel, Field
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


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PlanRequest(BaseModel):
    name: str
    price: float
    features: str


class SubscribeRequest(BaseModel):
    user_id: int
    plan_id: int
    start_date: str
    end_date: str


class JobEvaluation(BaseModel):
    id: str
    score: int
    summary: str
    Verdict: str
    Gaps: str
    Hard_blockers: str = Field(alias="Hard blockers")
    What_makes_Fabien_stand_out: str = Field(alias="What makes Fabien stand out")
    Salary_target: str = Field(alias="Salary target")
    Recommendation: str
    
    class Config:
        populate_by_name = True  # Allow both alias and field name
