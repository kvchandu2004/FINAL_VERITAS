from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
# Add to User model
from sqlalchemy.orm import relationship
# In User class, add:
# 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'author' or 'editor'
    affiliation = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    manuscripts = relationship("Manuscript", back_populates="author")
    assigned_reports = relationship("AnalysisReport", back_populates="editor")