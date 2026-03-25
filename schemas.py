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


class ValidateRequest(BaseModel):
    token: str


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
    Hard_blockers: Optional[str] = Field(None, alias="Hard blockers")
    Stand_out: Optional[str] = Field(None, alias="Stand out")
    Salary_target: Optional[str] = Field(None, alias="Salary target")
    Recommendation: Optional[str] = None
    # Allow extra fields from LLM (matched_skills, missing_skills, etc.)
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True  # Allow both alias and field name
        extra = "allow"  # Allow extra fields from LLM response
