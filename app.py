from flask import Flask, redirect, url_for, session
from routes.auth_routes import auth_bp
from routes.panel_routes import panel_bp
from routes.shill_routes import shill_bp
from routes.tweets_routes import tweets_bp
from routes.metricas_routes import metricas_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Registrar todos los blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(panel_bp)
app.register_blueprint(shill_bp)
app.register_blueprint(tweets_bp)
app.register_blueprint(metricas_bp)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('panel.dashboard'))
    return redirect(url_for('auth.login'))



if __name__ == '__main__':
    app.run(debug=True)
