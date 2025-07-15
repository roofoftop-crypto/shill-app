from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from pyairtable import Table
import os
import asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import time

panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

@panel_bp.route('/')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('panel.html')

@panel_bp.route("/gestionar-grupos")
def gestionar_grupos():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    table_name = "Cuentas Telegram"
    table_grupos = "Grupos"

    print("→ DEBUG Airtable keys:")
    print("API KEY:", api_key)
    print("BASE ID:", base_id)
    print("TABLE NAME:", table_name)

    tabla = Table(api_key, base_id, table_name)
    tabla_grupos = Table(api_key, base_id, table_grupos)

    try:
        registros = tabla.all(formula="Activa = 1")
        print(f"→ Cantidad de registros activos encontrados: {len(registros)}")
        cuentas = []
        for r in registros:
            fields = r.get("fields", {})
            alias = fields.get("Alias")
            session_str = fields.get("Session")
            if alias and session_str:
                cuentas.append((alias, session_str))

        grupos_registros = tabla_grupos.all()
        grupos = []
        for g in grupos_registros:
            fields = g.get("fields", {})
            nombre = fields.get("Nombre")
            enlace = fields.get("Enlace")
            if nombre and enlace:
                grupos.append({"nombre": nombre, "enlace": enlace})

        print("→ Cuentas cargadas:", cuentas)
        print("→ Grupos cargados:", grupos)
        return render_template("gestionar_grupos.html", cuentas=cuentas, grupos=grupos)

    except Exception as e:
        print("⚠️ Error al consultar Airtable:", e)
        return render_template("gestionar_grupos.html", cuentas=[], grupos=[])

@panel_bp.route("/agregar-a-grupo", methods=["POST"])
def agregar_a_grupo():
    data = request.get_json()
    group = data.get("group")
    sessions = data.get("sessions", [])
    delay = int(data.get("delay", 10))

    if not group or not sessions:
        return jsonify({"status": "error", "message": "Faltan parámetros"}), 400

    results = []

    for session_str in sessions:
        try:
            client = TelegramClient(StringSession(session_str), os.environ.get("API_ID"), os.environ.get("API_HASH"))
            client.connect()
            if not client.is_user_authorized():
                try:
                    client.send_code_request(phone=os.environ.get("PHONE"))
                    return jsonify({"status": "error", "message": "Sesión requiere verificación 2FA"})
                except SessionPasswordNeededError:
                    return jsonify({"status": "error", "message": "Sesión requiere contraseña 2FA"})

            client(JoinChannelRequest(group))
            results.append({"session": session_str[:10] + "...", "status": "joined"})
            time.sleep(delay)
        except Exception as e:
            print("❌ Error con sesión:", session_str[:10], "-", e)
            results.append({"session": session_str[:10] + "...", "status": f"error: {str(e)}"})

        finally:
            if 'client' in locals():
                client.disconnect()

    return jsonify({"status": "ok", "results": results})
