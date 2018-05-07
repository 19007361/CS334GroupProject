from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from .models import User
from werkzeug import secure_filename
import os
import shutil

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if 'username' in session:
        # A user has already logged on
        return redirect(url_for('profile', name=session['username']))
    else:
        if request.method == 'POST':
            if "loginUser" in request.form:
                #Login
                username = request.form['loginUN']
                username = username.lower()
                passw = request.form['loginPass']
                if User(username).checkPass(passw):
                    session['username']=username
                    return redirect(url_for('profile', name=username)) #redrects to profile page
                else:
                    flash('Your username and or password was incorrect or does not exist')
            else:
                #Registration
                passValid = request.form['p1']
                userValid = ((request.form['username']).replace(" ", "")).lower()
                if (any(num.isdigit() for num in passValid) and any(char.isupper() for char in passValid) and userValid.isalnum() and len(passValid) >= 8):
                    if request.form['p1'] == request.form['p2']:
                        #pass same
                        username = userValid
                        name = request.form['name']
                        passw = request.form['p1']
                        email = request.form['email']
                        cbs = ['cbPsychology' in request.form, 'cbTravel' in request.form, 'cbEntertainment' in request.form, 'cbFood' in request.form, 'cbHobbies' in request.form, 'cbNightlife' in request.form, 'cbScience' in request.form]
                        #print(cbs)
                        #^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$ email regex
                        if User(username).addUser(passw, email, name, cbs):
                            session['username'] = username
                            return redirect(url_for('profile', name=username)) #redrects to profile page
                        else:
                            flash('This user already exists')
                    else:
                        flash('Passwords do not match')
                else:
                    flash('Password of incorrect format or username is not alphanumeric')
        return render_template('index.html') #if just a page get, then will return this page

@app.route('/p/<name>', methods=['GET','POST'])
def profile(name):
    edit = False
    original = False
    fllw = User(session['username']).getFollowed() #iffy about this here but fllw needs to exist before it can be assigned in updateFollowed
    bookmarkedQ = []
    noBMQ = 0
    suggestedUser = []
    noSU = 0
    if request.method == 'POST':
        if session['username'] == name:
            original = True
            if 'edit' in request.form:
                edit=True
            elif 'follow' in request.form:
                User(session['username']).followUser(request.form['follow'])
            else:
                User(session['username']).editBio(request.form['bioEdit'])
                cbs = ['cbPsychology' in request.form, 'cbTravel' in request.form, 'cbEntertainment' in request.form, 'cbFood' in request.form, 'cbHobbies' in request.form, 'cbNightlife' in request.form, 'cbScience' in request.form]
                User(session['username']).updateFollowed(cbs, fllw)
                if not len(request.form['p1']) == 0:
                    if request.form['p1'] == request.form['p2']:
                        User(session['username']).editPass(request.form['p1'])
                try:
                    file = request.files['file']
                except:
                    file = None
                if file and not file.filename == '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(os.path.dirname(__file__)+"/static/temp/", filename))
                    shutil.copy(os.path.dirname(__file__)+"/static/temp/"+filename, os.path.dirname(__file__)+"/static/Users/"+session['username']+".png")
                    os.unlink(os.path.dirname(__file__)+"/static/temp/"+filename)
    if session['username'] == name:
        original = True
        fllw = User(session['username']).getFollowed()
        #Bookmarked Questions
        bookmarkedQ, noBMQ = User(session['username']).getBookmarked()
        #Suggested Follow - OWN PROFILE ONLY
        suggestedUser, noSU = User(session['username']).suggestedFollow()

    return render_template('profile.html', me = User(session['username']).getMe(), other = User(session['username']).getOther(otherUser=name), currentUser = original, edit = edit, bio = "This is a test bio", noUpvote = User(session['username']).getTotUV(), fllw = fllw, bookmarkedQ=bookmarkedQ, noBMQ=noBMQ, suggestedUser = suggestedUser, noSU = noSU, name=name)

@app.route('/s/<query>', methods=['GET', 'POST'])
def search(query):
    if request.method == 'POST':
        if 'follow' in request.form:
            User(session['username']).followUser(request.form['follow'])
        elif 'unfollow' in request.form:
            User(session['username']).unfollowUser(request.form['unfollow'])

    results = []
    tag, text, n = User(session['username']).getSearch(query)
    usr, c = User(session['username']).getSearchUser(query)
    for i in range(n):
        r = [text[i][0], text[i][1], tag[i], text[i][2]]
        results.append(r)

    return render_template('search.html', me=User(session['username']).getMe(), results=results, noPosts=n, query=query, usr=usr, c=c)

@app.route('/q/<id>', methods=['GET','POST'])
def question(id):
    if request.method == 'POST':
        if 'textF' in request.form:
            if not len(request.form['textF']) == 0:
                User(session['username']).addReply(id, request.form['textF'])
        elif 'uv' in request.form:
            User(session['username']).upvote(request.form['uv'])
        elif 'dv' in request.form:
            User(session['username']).downvote(request.form['dv'])
        elif 'ub' in request.form:
            User(session['username']).noBook(request.form['ub'])
        elif 'b' in request.form:
            User(session['username']).bookmark(request.form['b'])

    Qbody, user, tag, bookmarked = User(session['username']).getQuestion(id)
    mainQ = [Qbody['title'], Qbody['text'], user, Qbody['date'], tag, id]
    replies = []
    poster, ld, liked, c, cc = User(session['username']).getReplies(id)
    for i in range(c):
        replies.append([poster[i], ld[i][1], ld[i][0], liked[i], ld[i][2], cc[i]])
    return render_template('question.html', bookmarked = bookmarked, question=mainQ, replies = replies, noPosts=len(replies), me = User(session['username']).getMe())

@app.route('/addQ', methods=['GET','POST'])
def newquestion():
    if request.method == 'POST':
            if not len(request.form['textTitl']) == 0:
                if not len(request.form['textArea']) == 0:
                    cbs = ['cbPsychology' in request.form, 'cbTravel' in request.form, 'cbEntertainment' in request.form, 'cbFood' in request.form, 'cbHobbies' in request.form, 'cbNightlife' in request.form, 'cbScience' in request.form]
                    User(session['username']).addQuestion(request.form['textTitl'], cbs, request.form['textArea'])
                    return redirect(url_for('question', id=User(session['username']).findT(request.form['textTitl'])['id']))
    return render_template('newquestion.html', me = User(session['username']).getMe())

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/searchH', methods=['POST'])
def searchH():
    return redirect(url_for('search', query=request.form['sq']))
