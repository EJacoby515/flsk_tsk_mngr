import os
from flask import Flask, send_from_directory, request, jsonify, render_template, session
from config import Config
from models import db
from app.authentication.auth_routes import auth_bp
from app.site.site_routes import site_bp, cache_buster
from app.api.api_routes import api_bp
from flask_migrate import Migrate
import logging

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("GPT_API_KEY"))

app = Flask(__name__, static_folder='static')

def create_app():
    app.config.from_object(Config)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(site_bp, template_folder='site')
    app.register_blueprint(api_bp, template_folder='api')
    db.init_app(app)
    migrate = Migrate(app, db)

    # Disable caching for static files
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path, cache_timeout=0)

    # Make the cache_buster function available to Jinja templates
    app.context_processor(lambda: dict(cache_buster=cache_buster))

    app.secret_key = os.environ.get('SECRET_KEY')

    return app

def call_gpt_api(priority, title, status):
    # Prepare the prompt for the GPT API
    prompt = "Here are some tasks with their user-declared priorities, titles, and statuses:\n\n"
    for p, t, s in zip(priority, title, status):
        prompt += f"User Priority: {p.capitalize()}, Title: {t}, Status: {s}\n"

    prompt += "\nBased on the user-declared priorities, titles, and statuses, please suggest the optimal order for these tasks. The order should prioritize tasks with higher user-declared priorities (High > Medium > Low) and then consider the task titles and statuses for further ordering within each priority level. List the exact task titles in the suggested order, one per line, without any modifications or additions."
    logging.info(f'GPT API Prompt: {prompt}')

    # Call the GPT API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7
        )
    except Exception as e:
        logging.error(f'Error in GPT API call: {str(e)}')
        raise e

    # Extract the suggested order from the response
    suggested_order = response.choices[0].message.content.strip().split('\n')

    # Remove any numbered prefixes from the suggested order
    suggested_order = [title.split('. ', 1)[-1] for title in suggested_order]

    return suggested_order