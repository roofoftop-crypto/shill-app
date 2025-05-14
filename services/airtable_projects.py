import os
from pyairtable import Table

# Obtener variables desde entorno
API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

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
