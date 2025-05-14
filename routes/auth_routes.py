from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.auth_service import validate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('clave')
        user = validate_user(username, password)
        if user:
            session['username'] = user["username"]
            session['name'] = user["name"]
            flash(f"¡Bienvenido, {user['name']}!", "success")
            return redirect(url_for('panel.dashboard'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))