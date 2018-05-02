from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from .models import User

app = Flask(__name__)

def search(formData):
    quer = formData["searchQ"]


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
    #Edit the index html to make use of input groups

@app.route('/p')
def profile():
    return render_template('profile.html')

@app.route('/s')
def search():
    return render_template('search.html')

@app.route('/q')
def question():
    return render_template('question.html')

@app.route('/addQ')
def newquestion():
    return render_template('newquestion.html')
