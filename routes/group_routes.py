# routes/group_routes.py

import asyncio
import os
import time
from flask import Blueprint, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

group_bp = Blueprint('group', __name__)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

async def unir_a_grupo(session_string, group_username):
    async with TelegramClient(StringSession(session_string), API_ID, API_HASH) as client:
        await client(JoinChannelRequest(group_username))

@group_bp.route("/agregar-a-grupo", methods=["POST"])
def agregar_a_grupo():
    data = request.json
    sessions = data.get("sessions", [])  # lista de sesiones seleccionadas
    group = data.get("group")            # grupo público (@link)
    delay = int(data.get("delay", 10))   # delay entre uniones (segundos)

    if not sessions or not group:
        return jsonify({"error": "Faltan datos"}), 400

    resultados = []
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for idx, ses in enumerate(sessions):
        try:
            loop.run_until_complete(unir_a_grupo(ses, group))
            resultados.append({"session": ses, "status": "ok"})
        except Exception as e:
            resultados.append({"session": ses, "status": f"error: {str(e)}"})
        if idx < len(sessions) - 1:
            time.sleep(delay)

    return jsonify(resultados)
