from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from .models import User

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
                    flash('GET REKT!')
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
                        #^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$ email regex
                        if User(username).addUser(passw, email, name):
                            session['username'] = username
                            return redirect(url_for('profile', name=username)) #redrects to profile page
                        else:
                            flash('Somethang funk-a')
                    else:
                        flash('Nice Try')
                else:
                    flash('You fucked it') #lol, subject to change :P
        return render_template('index.html') #if just a page get, then will return this page

@app.route('/p/<name>', methods=['GET','POST'])
def profile(name):
    if request.method == 'POST':
        print("hi")
    return render_template('profile.html', me = User(session['username']).getMe())

@app.route('/s/<query>')
def search(query):
    results = []
    tag, text, n = User(session['username']).getSearch(query)
    for i in range(n):
        r = [text[i][0], text[i][1], tag[i], text[i][2]]
        results.append(r)
    return render_template('search.html', me=User(session['username']).getMe(), results=results, noPosts=len(results), query=query)

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
                    User(session['username']).addQuestion(request.form['textTitl'], request.form['topicSelect'], request.form['textArea'])
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
