from pyairtable import Table
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Variables del entorno
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

# Tabla de cuentas de Telegram en Airtable
table_sessions = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Cuentas Telegram")


def cargar_cuentas_activas():
    """Carga todas las cuentas activas desde Airtable."""
    records = table_sessions.all()
    cuentas = {}
    for r in records:
        fields = r["fields"]
        if fields.get("Activa") and "Alias" in fields and "Session" in fields:
            alias = fields["Alias"].strip()
            session_str = fields["Session"].strip()
            cuentas[alias] = session_str
    return cuentas


import asyncio
import random
import time
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from services.configuracion_shill import obtener_configuracion_shill
from services.telegram_manager import cargar_cuentas_activas
from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

def verificar_sesiones(cuentas):
    """
    Recibe un dict de {alias: string_session} y devuelve {alias: True/False}.
    Agrega validación y debug por consola.
    """
    estados = {}

    for alias, session_str in cuentas.items():
        client = None
        try:
            print(f"🔍 Verificando alias {alias}...")

            # Validación rápida
            if not session_str or len(session_str) < 100:
                print(f"⚠️ Sesión de {alias} es inválida o demasiado corta.")
                estados[alias] = False
                continue

            # Manejo de event loop
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            client.connect()

            autorizado = client.is_user_authorized()
            estados[alias] = autorizado
            print(f"✅ Alias {alias} está autorizado: {autorizado}")

        except Exception as e:
            print(f"❌ Error verificando alias {alias}: {e}")
            estados[alias] = False

        finally:
            if client:
                client.disconnect()

    return estados
