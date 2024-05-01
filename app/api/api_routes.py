from flask import Blueprint, jsonify, request, session, render_template, url_for, flash, redirect
from config import get_db_connection
from models import Task, task_schema
from datetime import datetime, timezone

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database.'}), 500
    
    print('Database connection established')

    if request.method == 'GET':
        user_id = request.args.get('user_id')
        print(f'User ID from query parameter: {user_id}')
        cur = conn.cursor()
        cur.execute('SELECT * FROM task WHERE user_id = %s', (user_id,))
        tasks_data = cur.fetchall()
        print(f'Tasks data from database: {tasks_data}')
        tasks = []
        for task in tasks_data:
            task_dict = dict(zip(Task.__table__.columns.keys(), task))
            task_obj = Task(**task_dict)
            tasks.append(task_schema.dump(task_obj))
        cur.close()
        return jsonify(tasks)

    elif request.method == 'POST':
        print("POST request received")
        user_id = session.get('user_id')
        if not user_id:
            flash('User not authenticated', 'error')
            return redirect(url_for('auth.login'))

        title = request.form.get('title').strip()
        description = request.form.get('description')
        priority = request.form.get('priority')
        status = request.form.get('status')

        new_task = Task(user_id=user_id, title=title, description=description,
                        priority=priority, status=status)
        print(f"New task: {new_task.__dict__}")
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO task (user_id, title, description, priority, status, created_at, modified_at, "AI_Arranged") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                        (new_task.user_id, new_task.title, new_task.description, new_task.priority, new_task.status, datetime.now(timezone.utc), datetime.now(timezone.utc), 0))
            print("SQL query executed")
            conn.commit()
            print("Changes committed to the database")
            flash('Task added successfully', 'task')
            return redirect(url_for('site.tasks'))
        except Exception as e:
            print(f'Error executing SQL query: {e}')
            conn.rollback()
            flash('Failed to create task', 'error')
            return redirect(url_for('site.tasks'))

@api_bp.route('/api/tasks/<task_id>', methods=['GET', 'PUT', 'DELETE', 'POST'])
def task(task_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database.'}), 500

    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute('SELECT * FROM task WHERE id = %s', (task_id,))
        task_data = cur.fetchone()
        if task_data:
            task_dict = dict(zip(Task.__table__.columns.keys(), task_data))
            task = Task(**task_dict)
            result = task_schema.dump(task)
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Task not found.'}), 404

    elif request.method == 'PUT':
        data = request.get_json()
        try:
            print(f"Executing SQL Query: UPDATE task SET title = '{data['title']}', description = '{data['description']}', priority = {data['priority']}, status = '{data['status']}' WHERE id = {task_id}")
            cur.execute("UPDATE task SET title = %s, description = %s, priority = %s, status = %s, modified_at = NOW() WHERE id = %s",
                        (data['title'], data['description'], data['priority'], data['status'], task_id))
            conn.commit()
            print("Changes committed to the database")

            # Retrieve the updated task from the database
            cur.execute("SELECT * FROM task WHERE id = %s", (task_id,))
            task_data = cur.fetchone()

            if task_data:
                task_dict = dict(zip(('id', 'user_id', 'title', 'description', 'priority', 'status', 'created_at', 'modified_at'), task_data))
                task = Task(**task_dict)
                result = task_schema.dump(task)
                return jsonify(result), 200
            else:
                return jsonify({'message': 'Task not found.'}), 404

        except Exception as e:
            print(f"Error executing SQL query: {e}")
            conn.rollback()
            return jsonify({'message': 'Failed to update task.'}), 500

        finally:
            cur.close()
            conn.close()

    elif request.method == 'POST':
        if request.form.get('_method')  == 'DELETE':
            cur.execute('DELETE FROM task WHERE id = %s', (task_id,))
            conn.commit()
            cur.close()
            conn.close()
            flash('Task deleted successfully','success')
            return redirect(url_for('site.tasks'))
        else:
            return jsonify({'error': 'Invalid request.'}), 400

@api_bp.route('/api/tasks/edit/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database.'}), 500

    cur = conn.cursor()

    if request.method == 'GET':
        print('Connected to DB, retrieving Task data')
        cur.execute('SELECT * FROM task WHERE id = %s', (task_id,))
        task_data = cur.fetchone()
        print(task_data)
        if task_data:
            task_dict = dict(zip(Task.__table__.columns.keys(), task_data))
            return render_template('edit_task.html', task=task_dict)
        else:
            flash('Task not found', 'error')
            return redirect(url_for('site.tasks'))

    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        status = request.form.get('status')

        cur.execute("UPDATE task SET title = %s, description = %s, priority = %s, status = %s, modified_at = NOW() WHERE id = %s",
                    (title, description, priority, status, task_id))
        conn.commit()
        cur.close()
        conn.close()
        flash('Task updated successfully', 'task')
        return redirect(url_for('site.tasks'))