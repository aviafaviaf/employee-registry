from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from employee_registry.db.connection import get_session
from employee_registry.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse,
    EmployeeFilter
)
from employee_registry.services.employee_service import EmployeeService, calculate_age


logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/employees", tags=["Employees"])

@api_router.get(
    "/",
    response_model=EmployeeListResponse,
    summary="Получить список сотрудников",
    description="""
    Возвращает список сотрудников с возможностью фильтрации и пагинации.
    """
)
def get_employees(
    search: Optional[str] = Query(None, description="Поиск по ФИО или телефону"),
    is_male: Optional[bool] = Query(None, description="Фильтр по полу"),
    age_from: Optional[int] = Query(None, ge=0, le=120, description="Возраст от"),
    age_to: Optional[int] = Query(None, ge=0, le=120, description="Возраст до"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_session)
):
    """Получение списка сотрудников с фильтрацией"""
    filters = EmployeeFilter(
        search=search,
        is_male=is_male,
        age_from=age_from,
        age_to=age_to,
        page=page,
        size=size
    )

    service = EmployeeService(db)
    employees, total = service.get_all(filters)

    items = []
    for emp in employees:
        employee_data = EmployeeResponse.model_validate(emp)
        employee_data.age = calculate_age(emp.birth_date)
        items.append(employee_data)

    total_pages = (total + size - 1) // size if total > 0 else 0

    return EmployeeListResponse(
        total=total,
        items=items,
        page=page,
        size=size,
        pages=total_pages
    )


@api_router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Получить сотрудника по ID",
    responses={
        404: {"description": "Сотрудник не найден"}
    }
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_session)
):
    """Получение информации о сотруднике по ID"""
    service = EmployeeService(db)
    employee = service.get_by_id(employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )

    response = EmployeeResponse.model_validate(employee)
    response.age = calculate_age(employee.birth_date)

    return response


@api_router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового сотрудника",
    responses={
        400: {"description": "Ошибка валидации или сотрудник уже существует"},
        422: {"description": "Ошибка валидации данных"}
    }
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_session)
):
    """Создание нового сотрудника"""
    try:
        service = EmployeeService(db)
        employee = service.create(employee_data)

        response = EmployeeResponse.model_validate(employee)
        response.age = calculate_age(employee.birth_date)

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@api_router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Обновить сотрудника",
    responses={
        404: {"description": "Сотрудник не найден"},
        400: {"description": "Ошибка валидации"}
    }
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_session)
):
    """Обновление данных сотрудника"""
    try:
        service = EmployeeService(db)
        employee = service.update(employee_id, employee_data)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сотрудник с ID {employee_id} не найден"
            )

        response = EmployeeResponse.model_validate(employee)
        response.age = calculate_age(employee.birth_date)

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

@api_router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сотрудника",
    responses={
        404: {"description": "Сотрудник не найден"},
        204: {"description": "Успешное удаление"}
    }
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_session)
):
    """Удаление сотрудника по ID"""
    service = EmployeeService(db)
    deleted = service.delete(employee_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )

    return None
