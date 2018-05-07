from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
from flask import url_for
import os
import uuid
import shutil

graph = Graph(username = "Database", password = "password")

def initDB():
    topics = ['Pschology', 'Travel', 'Entertainment', 'Food', 'Hobbies', 'Nightlife', 'Science']
    user = graph.find_one('Topic', 'topic', "Pschology")
    print(user)
    if user == None:
        for i in range(len(topics)):
            graph.create(Node("Topic", topic=topics[i]))
        print("DB initialized")
    else:
        print("DB was ready")

def date():
    return datetime.now().strftime('%Y-%m-%d')

class User:
    def __init__(self, username):
        self.username = username

    def getMe(self):
        return [self.username, self.find()['fullName'], self.find()['bio']]

    def find(self):
        user = graph.find_one('User', 'username', self.username)
        return user

    def getOther(self, otherUser):
        other = graph.find_one('User', 'username', otherUser)
        return [otherUser, other['fullName'], other['bio']]

    def findT(self, term):
        user = graph.find_one('Question', 'title', term)
        return user

    def findByID(self, term):
        user = graph.find_one('Question', 'id', term)
        return user

    def getFollowed(self):
        q = "MATCH (u:User)-[:LIKES]->(n:Topic) WHERE u.username={user} return n"
        topics = ['Pschology', 'Travel', 'Entertainment', 'Food', 'Hobbies', 'Nightlife', 'Science']
        out = [False, False, False, False, False, False, False]
        for record in graph.run(q, user=self.username):
            for i in range(len(topics)):
                if topics[i] == record['n']['topic']:
                    out[i] = True
        return [topics, out]

    def updateFollowed(self, cbs, fllw):
        a = "MATCH (u:User), (t:Topic) WHERE u.username={user} AND t.topic={top} CREATE (u)-[:LIKES]->(t)"
        r = "MATCH(u:User)-[r:LIKES]-(t:Topic) WHERE u.username={user} AND t.topic={top} DELETE r"
        for i in range(len(cbs)):
            if cbs[i]:
                if not fllw[1][i] == True:
                    graph.run(a, user=self.username, top=fllw[0][i])
            else:
                if not fllw[1][i] == False:
                    graph.run(r, user=self.username, top=fllw[0][i])

    def editBio(self, bio):
        q = "MATCH(u:User) WHERE u.username={user} SET u.bio = {bio} RETURN u"
        graph.run(q, user=self.username, bio=bio)

    def editPass(self, passw):
        q = "MATCH(u:User) WHERE u.username={user} SET u.password = {pa} RETURN u"
        graph.run(q, user=self.username, pa=bcrypt.encrypt(passw))

    def getTotUV(self):
        q = "match (u:User)-[:ANSWERED]-(r:Reply) where u.username = {user} OPTIONAL MATCH (b:User)-[e:UPVOTED]-(r) rETURN count(b) AS cnt, r"
        tot = 0
        for record in graph.run(q, user=self.username):
            tot += record['cnt']
        return tot

    def suggestedFollow(self):
        #This function is only visible on one's own profile, hence self.username used
        q = "MATCH (u:User), (i:User) WHERE i.username = {user} AND NOT u.username = {user} AND NOT (u)<-[:FOLLOWS]-(i) OPTIONAL MATCH (c:User)-[:UPVOTED]->(r:Reply) WHERE (u)-[:ANSWERED]->(r) RETURN u, count(c) as cnt ORDER BY cnt DESC LIMIT 5"
        out = []
        c= 0
        for res in graph.run(q, user=self.username):
            out.append([res['u']['username'], res['u']['fullName'], res['cnt']])
            c += 1
        return out, c

    def addUser(self, password, email, name, cbs):
        if not self.find():
            #move file
            shutil.copy(os.path.dirname(__file__)+"/static/defaultProf.png", os.path.dirname(__file__)+"/static/Users/"+self.username+".png")
            user = Node("User", username=self.username, password=bcrypt.encrypt(password), email=email, fullName=name, bio="")
            graph.create(user)

            topics = ['Pschology', 'Travel', 'Entertainment', 'Food', 'Hobbies', 'Nightlife', 'Science']
            for i in range(len(cbs)):
                if cbs[i]:
                    topic = graph.find_one('Topic', 'topic', topics[i])
                    graph.create(Relationship(user, "LIKES", topic))

            return True
        else:
            return False

    def checkPass(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def addQuestion(self, title, tag, text):
        user = self.find()
        topics = ['Pschology', 'Travel', 'Entertainment', 'Food', 'Hobbies', 'Nightlife', 'Science']
        post = Node(
                "Question",
                id=str(uuid.uuid4()),
                title=title,
                text=text,
                date=date()
        )
        for i in range(len(tag)):
            if tag[i] == True:
                topic = graph.find_one('Topic', 'topic', topics[i])
                graph.create(Relationship(post, "TAGGED", topic))

        rel = Relationship(user, "ASKED", post)
        graph.create(rel)

    def addReply(self, title, text):
        user = self.find()
        quest = graph.find_one('Question', 'id', title)
        post = Node(
                "Reply",
                id=str(uuid.uuid4()),
                text=text,
                date=date()
        )
        graph.create(post)
        graph.create(Relationship(user, "ANSWERED", post))
        graph.create(Relationship(post, "REPLYTO", quest))

    def upvote(self, rID):
        user = self.find()
        rep = graph.find_one('Reply', 'id', rID)
        graph.create(Relationship(user, "UPVOTED", rep))

    def downvote(self, rID):
        q = "MATCH(u:User)-[r:UPVOTED]-(p:Reply) WHERE u.username={user} AND p.id={post} DELETE r"
        graph.run(q, user=self.username, post=rID)

    def bookmark(self, qID):
        user = self.find()
        rep = graph.find_one('Question', 'id', qID)
        graph.create(Relationship(user, "BOOKMARKED", rep))

    def noBook(self, qID):
        q = "MATCH(u:User)-[r:BOOKMARKED]-(p:Question) WHERE u.username={user} AND p.id={post} DELETE r"
        graph.run(q, user=self.username, post=qID)

    def getBookmarked(self):
        f = "MATCH (u:User)-[:BOOKMARKED]->(q:Question) WHERE u.username={user} RETURN q"
        out = []
        c=0
        for res in graph.run(f, user=self.username):
            u = [res['q']['title'], res['q']['id']]
            out.append(u)
            c +=1
        return out, c

    def getQuestion(self, quer):
        whoAsked = "MATCH(n:User)-[:ASKED]->(m:Question) WHERE m.id = {quer} RETURN n.username"
        tagged = "MATCH(n:Topic)<-[:TAGGED]-(m:Question) WHERE m.id = {quer} RETURN n.topic as o"
        book = "match(u:User), (q:Question) WHERE u.username={user} AND q.id={title} RETURN EXISTS((u)-[:BOOKMARKED]-(q))"
        user = graph.run(whoAsked, quer=quer).evaluate()
        #tag = graph.run(tagged, quer = quer).evaluate()
        ii = []
        for res in graph.run(tagged, quer=quer):
            ii.append(res['o'])
        tag = ', '.join(ii)
        bmrk = graph.run(book, user=self.username, title=quer).evaluate()
        quest = self.findByID(quer)
        return quest, user, tag, bmrk

    def getSearch(self, quer):
        tagged = "MATCH(n:Topic)<-[:TAGGED]-(m:Question) WHERE m.title = {quer} RETURN n.topic as o"
        res = "MATCH(n:Question) WHERE toLower(n.title) CONTAINS toLower({quer}) RETURN n ORDER BY n.date"
        tags = []
        ld = []
        c = 0
        for record in graph.run(res, quer=quer):
            a = [record['n']['title'], record['n']['text'], record['n']['id']]
            ld.append(a)
            ii = []
            for res in graph.run(tagged, quer=record['n']['title']):
                ii.append(res['o'])
            tags.append(', '.join(ii))
            #tags.append(graph.run(tagged, quer = record['n']['title']).evaluate())
            c += 1
        return tags, ld, c

    def getSearchUser(self, quer):
        res = "MATCH(n:User) WHERE toLower(n.username) CONTAINS toLower({quer}) AND NOT n.username={slf} RETURN n"
        fll = "match(u:User), (q:User) WHERE u.username={user} AND q.username={text} RETURN EXISTS((u)-[:FOLLOWS]->(q))"
        out = []
        c = 0
        for record in graph.run(res, quer=quer, slf=self.username):
            out.append([record['n']['username'], record['n']['fullName'], record['n']['bio'], graph.run(fll, user=self.username, text=record['n']['username']).evaluate() ])
            c += 1
        return out, c

    def followUser(self, other):
        user = self.find()
        uu = graph.find_one('User', 'username', other)
        graph.create(Relationship(user, "FOLLOWS", uu))

    def unfollowUser(self, other):
        q = "MATCH(u:User)-[r:FOLLOWS]-(p:User) WHERE u.username={user} AND p.username={post} DELETE r"
        graph.run(q, user=self.username, post=other)

    def getReplies(self, quest):
        #res = "MATCH (n:Reply)-[:REPLYTO]->(m:Question) WHERE m.id = {quer} RETURN n ORDER BY n.date"
        res = "MATCH (n:Reply)-[:REPLYTO]->(m:Question) WHERE m.id = {quer} optional MATCH (u:User)-[r:UPVOTED]-(n:Reply)  RETURN n, COUNT(u) ORDER BY COUNT(u) DESC"
        r = "MATCH(n:User)-[:ANSWERED]->(m:Reply) WHERE m.id = {quer} RETURN n.username"
        book = "match(u:User), (q:Reply) WHERE u.username={user} AND q.id={text} RETURN EXISTS((u)-[:UPVOTED]-(q))"
        cnt = "match(u:User)-[r:UPVOTED]-(m:Reply) WHERE m.id={id} RETURN COUNT(u)"
        poster = []
        ld = []
        liked = []
        c = 0
        cc =[]
        for record in graph.run(res, quer=quest):
            a = [record['n']['date'], record['n']['text'], record['n']['id']]
            ld.append(a)
            cc.append(graph.run(cnt, id=record['n']['id']).evaluate())
            poster.append(graph.run(r, quer=record['n']['id']).evaluate())
            liked.append(graph.run(book, user=self.username, text = record['n']['id']).evaluate())
            c += 1
        return poster, ld, liked, c, cc
