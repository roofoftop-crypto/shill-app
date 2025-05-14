from flask import Blueprint, render_template, session, redirect, url_for, flash

metricas_bp = Blueprint('metricas', __name__, url_prefix='/metricas')

@metricas_bp.route('/')
def metricas_home():
    if 'username' not in session:
        flash('Debes iniciar sesión para acceder.', 'warning')
        return redirect(url_for('auth.login'))
    return "Sección Métricas (próximamente)"