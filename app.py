from flask import Flask, render_template, send_from_directory
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    
    db_connection = sqlite3.connect('captured_faces.db')
    cursor = db_connection.cursor()

    
    cursor.execute("SELECT * FROM captured_faces")
    entries = cursor.fetchall()

    
    db_connection.close()

    return render_template('index.html', entries=entries)

@app.route('/captured_faces/<path:filename>')
def captured_faces(filename):
    return send_from_directory('captured_faces', filename)

if __name__ == '__main__':
    app.run(debug=True)
