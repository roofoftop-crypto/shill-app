from pyairtable import Table
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ✅ Obtener variables desde .env (no hardcodearlas)
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

print("API_KEY:", API_KEY)
print("BASE_ID:", BASE_ID)
print("TABLE_NAME:", TABLE_NAME)

# Crear instancia de la tabla
table = Table(API_KEY, BASE_ID, TABLE_NAME)


def obtener_proyectos():
    records = table.all()
    return [
        {
            "id": r["id"],
            "nombre": r["fields"].get("Nombre", ""),
            "alias": r["fields"].get("Alias", ""),
            "telegram": r["fields"].get("Telegram", "")
        }
        for r in records
    ]

def agregar_proyecto(nombre, alias, telegram):
    return table.create({
        "Nombre": nombre,
        "Alias": alias,
        "Telegram": telegram
    })

def eliminar_proyecto(record_id):
    return table.delete(record_id)