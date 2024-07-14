from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from sqlite3 import Error
import os

app = Flask(__name__, static_url_path='', static_folder='static')

DATABASE = 'todo.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    if conn:
        try:
            sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                            id integer PRIMARY KEY,
                                            title text NOT NULL,
                                            description text
                                        ); """
            conn.execute(sql_create_tasks_table)
        except Error as e:
            print(e)
        finally:
            conn.close()

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/task', methods=['POST'])
def add_task():
    conn = create_connection()
    task = (request.json['title'], request.json.get('description', ''))
    sql = ''' INSERT INTO tasks(title,description)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    conn.close()
    return jsonify({'id': cur.lastrowid})

@app.route('/task/<int:id>', methods=['PUT'])
def update_task(id):
    conn = create_connection()
    task = (request.json['title'], request.json.get('description', ''), id)
    sql = ''' UPDATE tasks
              SET title = ? ,
                  description = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    conn.close()
    return jsonify({'updated': True})

@app.route('/task/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = create_connection()
    sql = 'DELETE FROM tasks WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
    conn.close()
    return jsonify({'deleted': True})

if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0')
