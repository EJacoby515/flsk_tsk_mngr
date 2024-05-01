from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.authentication.firebase_auth import auth
from config import get_db_connection
from models import User, db
import logging


auth_bp = Blueprint('auth', __name__, template_folder='auth_templates')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user['localId']
            session['user_id'] = uid
            session['user'] = uid
            
            return redirect(url_for('site.index'))
        except Exception as e:
            logging.error(f'Login failed: {str(e)}')
            flash('Invalid email or password, please try again.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        birthdate = request.form.get('birthdate')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            uid = user['localId']

            conn = get_db_connection()

            if conn is None:
                logging.error('Failed to establish database connection')
                flash('Failed to sign up. Please try again later.', 'error')
                return redirect(url_for('auth.signup'))

            cur = conn.cursor()

            cur.execute('INSERT INTO "user" (id, email, firstname, lastname) VALUES(%s, %s, %s, %s)',
                        (uid, email, firstname, lastname))
            conn.commit()
            conn.close()

            session['user_id'] = uid
            session['user'] = uid

            return redirect(url_for('site.index'))
        except Exception as e:
            logging.error(f'Signup failed: {str(e)}')
            if 'EMAIL_EXISTS' in str(e):
                flash('User already exists. Please log in.', 'warning')
            else:
                flash('Failed to sign up. Please try again.', 'error')
            return redirect(url_for('auth.signup'))
    return render_template('login.html', signup=True)

@auth_bp.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('auth.login')) 