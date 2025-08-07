from pydantic import BaseModel
from datetime import date

class EntryBase(BaseModel):
    date: date
    type: str
    category: str
    amount: float

class EntryCreate(EntryBase):
    pass

class Entry(EntryBase):
    id: int
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str
