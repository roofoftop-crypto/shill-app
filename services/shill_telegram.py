# --- app/services/shill_telegram.py ---

import json
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

import os

API_ID = int(os.environ.get("TELEGRAM_API_ID"))
API_HASH = os.environ.get("TELEGRAM_API_HASH")

SESSIONS_FILE = "app/data/sesiones.json"  # <-- Guardalo aquí

# Grupo fijo (podés usar @alias o ID numérico con -100...)
GRUPO_TELEGRAM = "@nombre_de_tu_grupo"

def cargar_sesiones():
    with open(SESSIONS_FILE, "r") as f:
        return json.load(f)

async def enviar_conversacion(texto, proyecto="Desconocido"):
    sesiones = cargar_sesiones()
    lineas = texto.strip().split("\n")
    mensajes = []

    for linea in lineas:
        if ":" in linea:
            sesion_tag, mensaje = linea.split(":", 1)
            sesion_tag = sesion_tag.strip()
            mensaje = mensaje.strip()
            if sesion_tag in sesiones:
                mensajes.append((sesion_tag, mensaje))
            else:
                print(f"⚠️ Sesión '{sesion_tag}' no encontrada. Ignorada.")

    for sesion_tag, mensaje in mensajes:
        print(f"📤 Enviando como {sesion_tag}: {mensaje}")
        string_session = sesiones[sesion_tag]

        try:
            async with TelegramClient(StringSession(string_session), API_ID, API_HASH) as client:
                await client.send_message(GRUPO_TELEGRAM, mensaje)
        except Exception as e:
            print(f"❌ Error enviando como {sesion_tag}: {e}")
