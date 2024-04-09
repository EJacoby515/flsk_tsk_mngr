from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.authentication.firebase_auth import auth
import logging

auth_bp = Blueprint('auth',  __name__, template_folder= 'auth_templates')

@auth_bp.route('/login', methods =  ['POST','GET'])
def login():
    if request.method == 'POST':
        email =  request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password (email, password)
            session['user']  =  email
            return redirect(url_for('site.index'))
        except Exception as e:
            logging.error(f'login failed: {str(e)}')
            flash ('Invalid email or password, please try again.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/signup', methods = ['POST','GET'])
def signup():
    if request.method == 'POST':
        email =  request.form.get('email')
        password  = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = email
            return redirect(url_for('site.index'))
        except:
            return 'Failed to sign up'
    return render_template('login.html',  signup  = True)

@auth_bp.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('auth.login'))