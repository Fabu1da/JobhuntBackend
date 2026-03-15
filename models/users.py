from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    username: str
    email: str
    password_hash: str

class subscription(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    user_id: int
    plan: str
    start_date: str
    end_date: str

class plan(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    name: str
    price: float
    features: str