from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    username: str
    email: str
    password_hash: str