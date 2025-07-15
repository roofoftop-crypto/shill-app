# File: /routes/panel_routes.py

from flask import Blueprint, render_template, session, redirect, url_for

panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

@panel_bp.route('/')
def dashboard():
    # Protege el acceso: si no hay sesion, redirige a login
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('panel.html')

@panel_bp.route("/gestionar-grupos")
def gestionar_grupos():
    with open("perfiles_sessions_actualizado.txt", "r", encoding="utf-8") as f:
        lineas = f.readlines()
        cuentas = [line.strip().split("::") for line in lineas if "::" in line]
    return render_template("gestionar_grupos.html", cuentas=cuentas)