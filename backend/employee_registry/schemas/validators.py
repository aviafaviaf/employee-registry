# employee_registry/schemas/validators.py

import re
from datetime import date
from typing import Optional

def validate_phone(v: str) -> str:
    """Валидация номера телефона"""
    cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
    if not cleaned.isdigit():
        raise ValueError('Телефон должен содержать только цифры')
    if len(cleaned) < 10 or len(cleaned) > 15:
        raise ValueError('Телефон должен содержать от 10 до 15 цифр')
    return v

def validate_optional_phone(v: Optional[str]) -> Optional[str]:
    """Валидация опционального номера телефона"""
    if v is None:
        return v
    return validate_phone(v)

def validate_birth_date(v: date) -> date:
    """Валидация даты рождения"""
    if v > date.today():
        raise ValueError('Дата рождения не может быть в будущем')
    return v

def validate_optional_birth_date(v: Optional[date]) -> Optional[date]:
    """Валидация опциональной даты рождения"""
    if v is None:
        return v
    return validate_birth_date(v)
