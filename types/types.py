from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class PlanRequest(BaseModel):
    name: str
    price: float
    features: str