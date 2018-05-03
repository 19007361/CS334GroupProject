from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from .models import User

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    #TODO: Richard
    if 'username' in session:
        # A user has already logged on
        return redirect(url_for('profile', name=session['username']))
    else:
        if request.method == 'POST':
            if "loginUser" in request.form:
                #Login
                username = request.form['loginUN']
                passw = request.form['loginPass']
                if User(username).checkPass(passw):
                    session['username']=username
                    return redirect(url_for('profile', name=username)) #redrects to profile page
                else:
                    flash("GET REKT!")
            else:
                #Registration
                if request.form['p1'] == request.form['p2']:
                    #pass same
                    username = request.form['username']
                    name = request.form['name']
                    passw = request.form['p1']
                    email = request.form['email']

                    if User(username).addUser(passw, email, name):
                        session['username'] = username
                        return redirect(url_for('profile', name=username)) #redrects to profile page
                    else:
                        flash("Somethang funk-a")
        return render_template('index.html') #if just a page get, then will return this page
        #Look up how flask flashing works to give user certain feedback
        #Edit the index html to make use of input groups

@app.route('/p/<name>', methods=['GET','POST'])
def profile(name):
    if request.method == 'POST':
        print("hi")
    return render_template('profile.html', me = [session['username'], "FULL"])

@app.route('/s/<query>')
def search(query):
    r1 = ["Title1", "Text1", "Topic1", "ID1"]
    r2 = ["Title2", "Text2", "Topic2", "ID2"]
    results = [r1, r2]
    return render_template('search.html', me=User(session['username']).getMe(), results=results, noPosts=len(results), query=query)

@app.route('/q/<id>')
def question(id):
    bookmarked = False
    mainQ = ["This is the title", "This is the question", "Username5", "01 Jan 2018", "Topic1"]
    q1 = ["Username2", "Reply text blah blah blah", "32 Oct 1999", True]
    q2 = ["Username3", "Reply text Hoop blah blah", "32 Nov 1999", False]
    q3 = ["Username4", "Reply text blah Good blah", "32 Dec 1999", False]
    replies = [q1, q2, q3, q2, q2]
    return render_template('question.html', bookmarked = bookmarked, question=mainQ, replies = replies, noPosts=len(replies), me = User(session['username']).getMe())

@app.route('/addQ')
def newquestion():
    return render_template('newquestion.html', me = User(session['username']).getMe())

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/searchH', methods=['POST'])
def searchH():
    return redirect(url_for('search', query=request.form['sq']))
