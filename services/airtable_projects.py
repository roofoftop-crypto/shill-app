import os
import time
from pyairtable import Table
from requests.exceptions import HTTPError

# Obtener variables desde entorno
API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

# Crear instancia de la tabla
table = Table(API_KEY, BASE_ID, TABLE_NAME)

from datetime import datetime, timedelta

_cache_proyectos = None
_cache_timestamp = None
_cache_duracion = timedelta(seconds=30)  # ajustable

def obtener_proyectos(max_reintentos=5):
    global _cache_proyectos, _cache_timestamp
    ahora = datetime.utcnow()

    if _cache_proyectos and _cache_timestamp and ahora - _cache_timestamp < _cache_duracion:
        return _cache_proyectos  # Devuelve cache si aún es válido

    for intento in range(max_reintentos):
        try:
            records = table.all(sort=["orden"])
            _cache_proyectos = [
                {
                    "id": r["id"],
                    "nombre": r["fields"].get("Nombre", ""),
                    "alias": r["fields"].get("Alias", ""),
                    "telegram": r["fields"].get("Telegram", "")
                }
                for r in records
            ]
            _cache_timestamp = ahora
            return _cache_proyectos
        except HTTPError as e:
            if e.response.status_code == 429:
                espera = 2 ** intento
                print(f"[AIRTABLE] Rate limit alcanzado. Reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise


def agregar_proyecto(nombre, alias, telegram, max_reintentos=5):
    for intento in range(max_reintentos):
        try:
            existing = table.all(sort=["orden"])
            nuevo_orden = len(existing) + 1
            return table.create({
                "Nombre": nombre,
                "Alias": alias,
                "Telegram": telegram,
                "orden": nuevo_orden
            })
        except HTTPError as e:
            if e.response.status_code == 429:
                espera = 2 ** intento
                print(f"[AIRTABLE] Rate limit alcanzado. Reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise

def eliminar_proyecto(record_id, max_reintentos=5):
    for intento in range(max_reintentos):
        try:
            return table.delete(record_id)
        except HTTPError as e:
            if e.response.status_code == 429:
                espera = 2 ** intento
                print(f"[AIRTABLE] Rate limit alcanzado. Reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise

