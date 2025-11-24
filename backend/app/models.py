from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'Operator', 'SiteManager', 'PM', 'Admin'
    created_at = Column(DateTime, default=datetime.utcnow)

    daily_logs = relationship("DailyLog", back_populates="user")

class DailyLog(Base):
    __tablename__ = "daily_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    workers_count = Column(Integer, nullable=False)
    tasks = Column(Text)
    hours_worked = Column(Float, nullable=False)
    equipment_used = Column(Text)
    fuel_consumed = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="daily_logs")

    documents = relationship("Document", back_populates="daily_log")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    ddt_number = Column(String, unique=True, nullable=False)
    packing_list = Column(Text)
    container_id = Column(String)
    batch_number = Column(String, nullable=False)
    non_conformity = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="material")

class ProjectProgress(Base):
    __tablename__ = "project_progress"
    id = Column(Integer, primary_key=True, index=True)
    kpi_name = Column(String, nullable=False)
    progress_percent = Column(Float, nullable=False)
    target_date = Column(DateTime)
    actual_date = Column(DateTime)
    notes = Column(Text)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    notes = Column(Text)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    log_id = Column(Integer, ForeignKey("daily_logs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="documents")
    daily_log = relationship("DailyLog", back_populates="documents")