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
            return redirect(url_for('profile', name="TEST")) #redrects to profile page
    return render_template('index.html') #if just a page get, then will return this page
    #Look up how flask flashing works to give user certain feedback
    #Edit the index html to make use of input groups

@app.route('/p/<name>')
def profile(name):
    return render_template('profile.html')

@app.route('/s/<query>')
def search(query):
    print(query)
    return render_template('search.html')

@app.route('/q/<id>')
def question(id):
    bookmarked = False
    mainQ = ["This is the title", "This is the question", "Username", "01 Jan 2018"]
    q1 = ["Username2", "Reply text blah blah blah", "32 Oct 1999", True]
    q2 = ["Username3", "Reply text Hoop blah blah", "32 Nov 1999", False]
    q3 = ["Username4", "Reply text blah Good blah", "32 Dec 1999", False]
    replies = [q1, q2, q3]
    currentUser = ["Username5", "My cool Name"]
    return render_template('question.html', bookmarked = bookmarked, question=mainQ, replies = replies, noPosts=len(replies), me = currentUser)

@app.route('/addQ')
def newquestion():
    return render_template('newquestion.html')
