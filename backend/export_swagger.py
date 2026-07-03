import json
from employee_registry.main import app

openapi_schema = app.openapi()

with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

print("Swagger сохранен в openapi.json")
