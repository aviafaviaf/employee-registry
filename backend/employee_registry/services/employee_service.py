import logging
from datetime import date
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from employee_registry.db.models import Employee
from employee_registry.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeFilter

logger = logging.getLogger(__name__)


def calculate_age(birth_date: date) -> int:
    """Вычисление возраста по дате рождения"""
    today = date.today()
    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


class EmployeeService:
    """Сервис для работы с сотрудниками"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: EmployeeCreate) -> Employee:
        """Создание нового сотрудника"""

        existing = self.db.query(Employee).filter(Employee.phone == data.phone).first()
        if existing:
            raise ValueError(f"Сотрудник с телефоном {data.phone} уже существует")

        employee = Employee(
            last_name=data.last_name,
            first_name=data.first_name,
            patronymic=data.patronymic,
            birth_date=data.birth_date,
            is_male=data.is_male,
            phone=data.phone,
            photo_base64=data.photo_base64
        )

        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        logger.info(
            "Создан сотрудник: {%s} {%s} (ID: {%s)",
            employee.last_name,
            employee.first_name,
            employee.id,
            exc_info=True
        )
        return employee

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Получение сотрудника по ID"""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_all(
        self,
        filters: EmployeeFilter
    ) -> Tuple[List[Employee], int]:
        """
        Получение списка сотрудников с фильтрацией и пагинацией
        Возвращает: (список сотрудников, общее количество)
        """
        query = self.db.query(Employee)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    func.concat(Employee.last_name, ' ',
                                Employee.first_name, ' ',
                                Employee.patronymic).ilike(search_term),
                    func.concat(Employee.last_name, ' ', Employee.first_name).ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.first_name.ilike(search_term),
                    Employee.patronymic.ilike(search_term),
                    Employee.phone.ilike(search_term)
                )
            )

        if filters.is_male is not None:
            query = query.filter(Employee.is_male == filters.is_male)

        if filters.age_from or filters.age_to:
            today = date.today()

            if filters.age_from is not None:
                max_birth_date = date(
                    today.year - filters.age_from,
                    today.month,
                    today.day
                )
                query = query.filter(Employee.birth_date <= max_birth_date)

            if filters.age_to is not None:
                min_birth_date = date(
                    today.year - filters.age_to - 1,
                    today.month,
                    today.day
                )
                query = query.filter(Employee.birth_date >= min_birth_date)
        total = query.count()

        offset = (filters.page - 1) * filters.size
        employees = query.order_by(
            Employee.last_name,
            Employee.first_name
        ).offset(offset).limit(filters.size).all()

        return employees, total

    def update(self, employee_id: int, data: EmployeeUpdate) -> Optional[Employee]:
        """Обновление сотрудника"""
        employee = self.get_by_id(employee_id)
        if not employee:
            return None

        if data.phone and data.phone != employee.phone:
            existing = self.db.query(Employee).filter(Employee.phone == data.phone).first()
            if existing:
                raise ValueError(f"Сотрудник с телефоном {data.phone} уже существует")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)

        self.db.commit()
        self.db.refresh(employee)

        logger.info(
            "Обновлен сотрудник: %s %s (ID: %s)",
            employee.last_name,
            employee.first_name,
            employee.id,
            exc_info=True,
        )
        return employee

    def delete(self, employee_id: int) -> bool:
        """Удаление сотрудника"""
        employee = self.get_by_id(employee_id)
        if not employee:
            return False

        self.db.delete(employee)
        self.db.commit()

        logger.info(
            "Удалён сотрудник: %s %s (ID: %s)",
            employee.last_name,
            employee.first_name,
            employee.id,
            exc_info=True,
        )
        return True
