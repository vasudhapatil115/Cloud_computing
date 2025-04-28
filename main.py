from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
CLOUD_STORAGE_FOLDER = 'cloud_storage'

db = SQLAlchemy(app)

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(CLOUD_STORAGE_FOLDER, exist_ok=True)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Home route
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    files = os.listdir(CLOUD_STORAGE_FOLDER)
    return render_template('index.html', files=files, user=session['user'])

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['user'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    if file and file.filename != '':
        cloud_path = os.path.join(CLOUD_STORAGE_FOLDER, file.filename)
        file.save(cloud_path)
    return redirect(url_for('home'))

# Download
@app.route('/download/<filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    return send_from_directory(CLOUD_STORAGE_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
