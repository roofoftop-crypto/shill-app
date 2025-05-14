from flask import Blueprint, render_template, session, redirect, url_for, flash

tweets_bp = Blueprint('tweets', __name__, url_prefix='/tweets')

@tweets_bp.route('/')
def tweets_home():
    if 'username' not in session:
        flash('Debes iniciar sesión para acceder.', 'warning')
        return redirect(url_for('auth.login'))
    return "Sección Tweets (próximamente)"