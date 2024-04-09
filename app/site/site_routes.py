from flask import Blueprint, render_template, session, redirect, url_for




site_bp  =  Blueprint('site',  __name__, template_folder= 'site_templates')


@site_bp.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('auth.login'))