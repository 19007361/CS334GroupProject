from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from .models import User, getPosts

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/p')
def profile():
    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            flash('Your username must have more than one character.')
        elif len(password) < 5:
            flash('Your password must meet criteria.')
        elif not User(username).register(password):
            flash('This user exists already')
        else:
            session['username'] = Username
            flash('Logged in.')
            return redirect(url_for('index'))
        return render_template('register.html')
