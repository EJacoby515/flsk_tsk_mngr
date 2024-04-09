from flask import Flask
from config import Config
from app.authentication.auth_routes import auth_bp
from app.site.site_routes import site_bp


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(auth_bp, url_prefix = '/auth')
app.register_blueprint(site_bp)

app.secret_key = 'secret'
