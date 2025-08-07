from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    type = Column(Enum('Income', 'Expense', name='entry_type'))
    category = Column(String)
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
