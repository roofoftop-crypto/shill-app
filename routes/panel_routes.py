from flask import Blueprint, render_template, session, redirect, url_for
from pyairtable import Table
import os

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
    table_name = "Cuentas Telegram"  # Corregido: esta es la tabla real

    print("→ DEBUG Airtable keys:")
    print("API KEY:", api_key)
    print("BASE ID:", base_id)
    print("TABLE NAME:", table_name)

    tabla = Table(api_key, base_id, table_name)

    try:
        registros = tabla.all(formula="Activa = 1")  # Filtra solo cuentas activas
        print(f"→ Cantidad de registros activos encontrados: {len(registros)}")
        cuentas = []
        for r in registros:
            print("→ Registro:", r)
            fields = r.get("fields", {})
            alias = fields.get("Alias")
            session_str = fields.get("Session")
            if alias and session_str:
                cuentas.append((alias, session_str))

        print("→ Cuentas cargadas:", cuentas)
        return render_template("gestionar_grupos.html", cuentas=cuentas)

    except Exception as e:
        print("⚠️ Error al consultar Airtable:", e)
        return render_template("gestionar_grupos.html", cuentas=[])
