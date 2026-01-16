from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    codes = relationship("Code", back_populates="project", cascade="all, delete")

class Code(Base):
    __tablename__ = 'codes'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    source_code = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Analysis results
    path_list = Column(Text)  # JSON serialized
    coverage_path = Column(Float)
    cyclomatic_complexity = Column(Integer)
    test_cases = Column(Text)  # JSON serialized

    project = relationship("Project", back_populates="codes")
