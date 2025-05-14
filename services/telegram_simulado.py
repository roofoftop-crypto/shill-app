import asyncio
import random
import time
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from services.configuracion_shill import obtener_configuracion_shill
from services.telegram_manager import cargar_cuentas_activas
from dotenv import load_dotenv
from pathlib import Path
from telethon import functions, types
import os


# Cargar .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")


def enviar_mensajes_simulados(texto, grupo_telegram):
    config = obtener_configuracion_shill()
    delay_min = config["delay_min"]
    delay_max = config["delay_max"]
    tiempo_max_conversacion = config["tiempo_max_conversacion"] * 3600

    usar_bloques = config.get("usar_bloques", False)
    mensajes_por_bloque = config.get("mensajes_por_bloque", 5)
    min_intervalo_bloque = config.get("min_intervalo_bloque", 15) * 60

    probabilidad_respuesta = config.get("probabilidad_respuesta", 0)
    probabilidad_reaccion = config.get("probabilidad_reaccion", 0)
    reacciones_posibles = config.get("reacciones", [])

    cuentas = cargar_cuentas_activas()
    respuestas = []

    bloques = texto.strip().split("\n")
    mensajes = []
    for linea in bloques:
        if ":" not in linea:
            continue
        tag, contenido = linea.split(":", 1)
        alias = tag.strip().replace("Session ", "")
        contenido = contenido.strip()
        mensajes.append((alias, contenido))

    inicio = time.time()
    contador_bloque = 0
    mensaje_anterior_id = None
    mensaje_anterior_texto = None
    alias_anterior = None

    for i, (alias, mensaje) in enumerate(mensajes):
        if time.time() - inicio > tiempo_max_conversacion:
            respuestas.append("🛑 Tiempo máximo de conversación alcanzado. Se detuvo el envío.")
            break

        session_str = cuentas.get(alias)
        if not session_str:
            respuestas.append(f"❌ Alias {alias} no encontrado o inactivo.")
            continue

        client = None
        try:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            client.connect()

            if not client.is_user_authorized():
                respuestas.append(f"❌ Alias {alias} no está autorizado.")
                continue

            es_mismo_alias = alias == alias_anterior

            reply_to_id = None
            if not es_mismo_alias and mensaje_anterior_id:
                if "?" in mensaje_anterior_texto:
                    reply_to_id = mensaje_anterior_id
                elif random.randint(1, 100) <= probabilidad_respuesta:
                    reply_to_id = mensaje_anterior_id

            if not es_mismo_alias:
                delay = random.uniform(delay_min, delay_max)
                with client.action(grupo_telegram, 'typing'):
                    time.sleep(delay)

            sent_msg = client.send_message(grupo_telegram, mensaje, reply_to=reply_to_id)
            respuestas.append(f"✅ {alias} envió: {mensaje}")

            mensaje_anterior_id = sent_msg.id
            mensaje_anterior_texto = mensaje

            # 🎉 Reacción automática usando otra cuenta
            reaccionador = None
            for otra_alias in cuentas.keys():
                if otra_alias != alias:
                    reaccionador = otra_alias
                    break

            if (
                reaccionador
                and reacciones_posibles
                and random.randint(1, 100) <= probabilidad_reaccion
            ):
                reaccion_session = cuentas.get(reaccionador)
                if reaccion_session:
                    try:
                        reaccion_client = TelegramClient(StringSession(reaccion_session), API_ID, API_HASH)
                        reaccion_client.connect()

                        if reaccion_client.is_user_authorized():
                            emoji = random.choice(reacciones_posibles)
                            reaccion_client(functions.messages.SendReactionRequest(
                                peer=grupo_telegram,
                                msg_id=mensaje_anterior_id,
                                reaction=[types.ReactionEmoji(emoji)]
                            ))
                            respuestas.append(f"❤️ {reaccionador} reaccionó con {emoji}")
                        reaccion_client.disconnect()
                    except Exception as e:
                        respuestas.append(f"⚠️ No se pudo agregar reacción: {e}")

        except Exception as e:
            respuestas.append(f"❌ Error con alias {alias}: {e}")
        finally:
            if client:
                client.disconnect()

        contador_bloque += 1
        if not es_mismo_alias:
            if usar_bloques and contador_bloque >= mensajes_por_bloque:
                respuestas.append(f"⏸️ Pausa de bloque: {min_intervalo_bloque // 60} minutos")
                time.sleep(min_intervalo_bloque)
                contador_bloque = 0

        alias_anterior = alias

    total_enviados = sum(1 for r in respuestas if r.startswith("✅"))
    return f"✅ Se enviaron {total_enviados} mensajes correctamente."
