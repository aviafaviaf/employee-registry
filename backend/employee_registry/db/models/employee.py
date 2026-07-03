from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean
from sqlalchemy.sql import func
from employee_registry.db import DeclarativeBase

class Employee(DeclarativeBase):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    first_name = Column(String(100), nullable=False, index=True)
    patronymic = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=False)
    is_male = Column(Boolean, nullable=False)
    phone = Column(String(20), nullable=True, unique=True, index=True)
    photo_base64 = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Employee(id={self.id}, full_name={self.last_name} {self.first_name})>"
