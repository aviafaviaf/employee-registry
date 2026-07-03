from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List

from employee_registry.schemas.validators import validate_optional_phone, validate_optional_birth_date, validate_phone, validate_birth_date


class EmployeeBase(BaseModel):
    """Базовые поля сотрудника"""
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")
    patronymic: Optional[str] = Field(None, max_length=100, description="Отчество")
    birth_date: date = Field(..., description="Дата рождения")
    is_male: bool = Field(..., description="Пол")
    phone: str = Field(..., description="Номер телефона")
    photo_base64: Optional[str] = Field(None, description="Фото в формате base64")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Валидация номера телефона"""
        return validate_phone(v)

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        return validate_birth_date(v)


class EmployeeCreate(EmployeeBase):
    """Создание сотрудника"""
    pass


class EmployeeUpdate(BaseModel):
    """Обновление сотрудника"""
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    is_male: Optional[bool] = None
    phone: Optional[str] = None
    photo_base64: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_optional_phone(v)

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        return validate_optional_birth_date(v)


class EmployeeResponse(EmployeeBase):
    """Ответ с сотрудником"""
    id: int
    age: Optional[int] = Field(None, description="Возраст в годах")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Ответ со списком сотрудников"""
    total: int = Field(..., description="Общее количество")
    items: List[EmployeeResponse] = Field(..., description="Список сотрудников")
    page: int = Field(1, description="Текущая страница")
    size: int = Field(20, description="Размер страницы")
    pages: int = Field(..., description="Всего страниц")


class EmployeeFilter(BaseModel):
    """Фильтры для поиска сотрудников"""
    search: Optional[str] = Field(None, description="Поиск по ФИО или телефону")

    is_male: Optional[bool] = Field(None, description="Фильтр по полу")

    age_from: Optional[int] = Field(None, ge=0, le=120, description="Возраст от")
    age_to: Optional[int] = Field(None, ge=0, le=120, description="Возраст до")

    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")
