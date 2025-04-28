from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure base uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
    os.makedirs(user_folder, exist_ok=True)
    files = os.listdir(user_folder)
    return render_template('index.html', files=files)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    file = request.files['file']
    if file:
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
        os.makedirs(user_folder, exist_ok=True)
        file.save(os.path.join(user_folder, file.filename))
        flash('File uploaded successfully!')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
    return send_from_directory(user_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
