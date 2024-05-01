from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from config import get_db_connection
from models import User, db, Task
import firebase_admin
from firebase_admin import auth
from app.authentication.firebase_auth import auth

def cache_buster():
    return str(datetime.now().timestamp())

site_bp  =  Blueprint('site',  __name__, template_folder= 'site_templates')
site_bp.add_app_template_filter(cache_buster, 'cache_buster')


def reorder_tasks(suggested_order, task_data):
    # Group tasks by priority and status
    tasks_by_priority_and_status = {
        'high': {'open': [], 'in progress': [], 'completed': []},
        'medium': {'open': [], 'in progress': [], 'completed': []},
        'low': {'open': [], 'in progress': [], 'completed': []}
    }

    print(f'Task data: {task_data}')

    for task in task_data:
        priority = task['priority'].lower()
        status = task['status'].lower()
        tasks_by_priority_and_status[priority][status].append(task)

        print(f'Tasks grouped by priority and status: {tasks_by_priority_and_status}')

    # Reorder tasks based on the suggested order within each priority and status category
    ordered_tasks = []
    for priority in ['high', 'medium', 'low']:
        for status in ['open', 'in progress']:
            tasks = tasks_by_priority_and_status[priority][status]
            suggested_tasks = [task for task in tasks if task['title'] in suggested_order]
            ordered_tasks.extend(suggested_tasks)

            # Add the remaining tasks that are not in the suggested order
            remaining_tasks = [task for task in tasks if task['title'] not in suggested_order]
            ordered_tasks.extend(remaining_tasks)

        # Add completed tasks for the current priority at the end
        ordered_tasks.extend(tasks_by_priority_and_status[priority]['completed'])

    return ordered_tasks

@site_bp.route('/suggested_order', methods=['POST'])
def suggested_order():
    from app import call_gpt_api
    data = request.get_json()
    priority = data['priority']
    title = data['title']
    status = data['status']

    try:
        suggested_order = call_gpt_api(priority, title, status)
        ordered_tasks = reorder_tasks(suggested_order, data)
        return jsonify({'success': True, 'ordered_tasks': ordered_tasks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@site_bp.route('/')
def index():
    user_id = None
    if 'user' in session:
        user_id = session['user']
        print(f'User_id: {user_id}')
    return render_template('landing.html', user_id = user_id)




@site_bp.route('/tasks')
def tasks():
    if 'user' in session:
        user_id = session['user']

        conn = get_db_connection()
        if conn is None:
            print('failed to connect to the database')
            flash('Failed to connect to the database.', 'error')
            return redirect(url_for('auth.login'))

        cur = conn.cursor()
        cur.execute('SELECT * FROM task WHERE user_id = %s ORDER BY "AI_Arranged" ASC, created_at DESC', (user_id,))
        user_tasks = cur.fetchall()
        cur.close()
        conn.close()

        if user_tasks:
            return render_template('tasks.html', tasks=user_tasks, user_id=user_id)
        else:
            flash('No tasks found.', 'info')
            return render_template('tasks.html', tasks=[], user_id=user_id)
    else:
        print('user is not logged in')
        flash('You need to be logged in to access tasks.', 'warning')
        return redirect(url_for('auth.login'))

@site_bp.route('/tasks/edit/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user' in session:
        user_id = session['user']

        conn = get_db_connection()
        if conn is None:
            flash('Failed to connect to the database.', 'error')
            return redirect(url_for('site.tasks'))

        cur = conn.cursor()

        cur.execute('SELECT * FROM task WHERE id = %s', (task_id,))
        task_data = cur.fetchone()

        if task_data:
            if request.method == 'POST':
                title = request.form.get('title')
                description = request.form.get('description')
                priority = request.form.get('priority')
                status = request.form.get('status')

                cur.execute("UPDATE task SET title = %s, description = %s, priority = %s, status = %s, modified_at = NOW() WHERE id = %s",
                            (title, description, priority, status, task_id))
                conn.commit()
                flash('Task updated successfully.', 'task')
                return redirect(url_for('site.tasks'))

            task_dict = dict(zip(Task.__table__.columns.keys(), task_data))
            task = Task(**task_dict)
            return render_template('edit_tasks.html', tasks=[task], user_id=user_id)
        else:
            cur.close()
            conn.close()
            flash('Task not found.', 'error')
            return redirect(url_for('site.tasks'))
    else:
        flash('You need to be logged in to edit a task.', 'warning')
        return redirect(url_for('auth.login'))

@site_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' in session:
        user_id = session['user']

        conn = get_db_connection()
        if conn is None:
            flash('Failed to connect to the database.','error')
            return redirect(url_for('site.index'))

        cur = conn.cursor()

        cur.execute('SELECT * FROM "user" WHERE id = %s',  (user_id,))
        user_data = cur.fetchone()

        if user_data:
            if request.method == 'POST':
                firstname = request.form.get('firstname')
                lastname=request.form.get('lastname')
                birthdate = request.form.get('birthdate')

                cur.execute('UPDATE "user" SET firstname = %s, lastname = %s, birthdate = %s where id = %s',
                            (firstname, lastname, birthdate, user_id))
                conn.commit()
                flash('Profile updated successfully.','profile')

            cur.close()
            conn.close()

            user = {
                'firstname': user_data[2],
                'lastname': user_data[3],
                'birthdate': user_data[4]
            }
            return render_template('profile.html', user = user, user_id = user_id)
        else:
            flash ('User not Found.', 'error')
            return redirect(url_for('auth.login'))
    else:
        flash('You need to be logged in to access your profile.',  'warning')
        return redirect(url_for('auth.login'))

@site_bp.route('/analytics')
def analytics():
    if 'user' in session:
        user_id = session['user']

        conn = get_db_connection()
        if conn is None:
            flash('Failed to connect to the database.', 'error')
            return redirect(url_for('site.index'))

        cur = conn.cursor()

        cur.execute('SELECT COUNT(*) FROM task WHERE user_id = %s AND status = %s', (user_id, 'open'))
        open_tasks_count = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM task WHERE user_id = %s AND status = %s', (user_id, 'in progress'))
        in_progress_tasks_count = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM task WHERE user_id = %s AND status = %s', (user_id, 'completed'))
        completed_tasks_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        return render_template('analytics.html', open_tasks_count=open_tasks_count,
                                in_progress_tasks_count=in_progress_tasks_count,
                                completed_tasks_count=completed_tasks_count)
    else:
        flash('You need to be logged in to access analytics.', 'warning')
        return redirect(url_for('auth.login'))
    

@site_bp.route('/ai_arrange', methods=['POST'])
def ai_arrange():
    from app import call_gpt_api  # Lazy import

    if 'user' in session:
        user_id = session['user']

        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to the database.'}), 500

        cur = conn.cursor()
        cur.execute('SELECT id, title, description, priority, status, created_at, modified_at FROM task WHERE user_id = %s AND status != %s', (user_id, 'completed'))
        tasks = cur.fetchall()


        print(f'Retrieved tasks from the database: {tasks}')
# Convert the tasks data to a list of dictionaries
        task_data = [
            {
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'priority': task[3],
                'status': task[4],
                'created_at': str(task[5]),
                'modified_at': str(task[6])
            }
            for task in tasks
        ]

        try:
            task_priorities = [task['priority'] for task in task_data]
            task_titles = [task['title'] for task in task_data]
            task_statuses = [task['status'] for task in task_data]


            suggested_order = call_gpt_api(task_priorities, task_titles, task_statuses)
            print(f"Suggested order: {suggested_order}")

            ordered_tasks = reorder_tasks(suggested_order, task_data)
            print(f'ORdered tasks: {ordered_tasks}')

            return jsonify({'success': True, 'ordered_tasks': ordered_tasks})

        except Exception as e:
            print(f"Error: {str(e)}")
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({'error': 'Failed to arrange tasks.'}), 500

    else:
        return jsonify({'error': 'User not authenticated.'}), 401