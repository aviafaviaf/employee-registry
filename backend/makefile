ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

ifndef APP_PORT
override APP_PORT = 8000
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif

APPLICATION_NAME = employee_registry
TEST = poetry run python -m pytest --verbosity=2 --showlocals --log-level=DEBUG
CODE = $(APPLICATION_NAME) tests

run:
	poetry run python3 -m $(APPLICATION_NAME).main

migrate:
	poetry run alembic upgrade head

make-migration:
	poetry run alembic revision --autogenerate 

open_db: 
	docker exec -it employee_registry_postgres psql -d $(POSTGRES_DB) -U $(POSTGRES_USER)
