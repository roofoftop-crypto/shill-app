# File: /routes/panel_routes.py

from flask import Blueprint, render_template, session, redirect, url_for

panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

@panel_bp.route('/')
def dashboard():
    # Protege el acceso: si no hay sesion, redirige a login
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('panel.html')