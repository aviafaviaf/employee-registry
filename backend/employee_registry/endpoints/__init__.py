from employee_registry.endpoints.employees import api_router as employees_router

list_of_routes = [
     employees_router,
]


__all__ = [
    "list_of_routes",
]
