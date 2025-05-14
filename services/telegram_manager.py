import os
import asyncio
import random
import time
from pathlib import Path
from pyairtable import Table
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from services.configuracion_shill import obtener_configuracion_shill
from services.telegram_manager import cargar_cuentas_activas

# Variables del entorno (Render las inyecta automáticamente)
API_ID = int(os.environ.get("TELEGRAM_API_ID"))
API_HASH = os.environ.get("TELEGRAM_API_HASH"))
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

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

            if not session_str or len(session_str) < 100:
                print(f"⚠️ Sesión de {alias} es inválida o demasiado corta.")
                estados[alias] = False
                continue

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
