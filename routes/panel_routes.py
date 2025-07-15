# File: /routes/panel_routes.py

from flask import Blueprint, render_template, session, redirect, url_for

panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

@panel_bp.route('/')
def dashboard():
    # Protege el acceso: si no hay sesion, redirige a login
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('panel.html')

from pyairtable import Table
import os


@panel_bp.route("/gestionar-grupos")
def gestionar_grupos():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    table_name = os.environ.get("AIRTABLE_TABLE_NAME")

    tabla = Table(api_key, base_id, table_name)
    registros = tabla.all()

    cuentas = []
    for r in registros:
        fields = r.get("fields", {})
        alias = fields.get("Alias")
        session = fields.get("Session")
        if alias and session:
            cuentas.append((alias, session))

    return render_template("gestionar_grupos.html", cuentas=cuentas)