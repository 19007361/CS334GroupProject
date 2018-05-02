from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from .models import User

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    #TODO: Richard
    if request.method == 'POST':
        print(request.form)
        print("loginUser" in request.form) # True if the login form
        if request.form['p1'] == request.form['p2']: #Applicable for only regsistration
            #pass same
            username = request.form['username']
            name = request.form['name']
            passw = request.form['p1']
            return redirect(url_for('profile')) #redrects to profile page
    return render_template('index.html') #if just a page get, then will return this page
    #Look up how flask flashing works to give user certain feedback

@app.route('/p')
def profile():
    return render_template('profile.html')

@app.route('/s')
def search():
    return render_template('search.html')

###########
'''

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')
'''
