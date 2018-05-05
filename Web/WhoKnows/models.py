from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
from flask import url_for
import os
import uuid
import shutil

graph = Graph(username = "Database", password = "password")

def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%Y-%m-%d')

class User:
    def __init__(self, username):
        self.username = username

    def getMe(self):
        return [self.username, self.find()['fullName']]

    def find(self):
        user = graph.find_one('User', 'username', self.username)
        return user

    def findT(self, term):
        user = graph.find_one('Question', 'title', term)
        return user

    def findByID(self, term):
        user = graph.find_one('Question', 'id', term)
        return user

    def addUser(self, password, email, name):
        if not self.find():
            #move file
            shutil.copy(os.path.dirname(__file__)+"/static/defaultProf.png", os.path.dirname(__file__)+"/static/Users/"+self.username+".png")
            user = Node("User", username=self.username, password=bcrypt.encrypt(password), email=email, fullName=name)
            graph.create(user)
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
        topic = graph.find_one('Topic', 'topic', tag)
        post = Node(
                "Question",
                id=str(uuid.uuid4()),
                title=title,
                text=text,
                date=date()
        )
        rel = Relationship(user, "ASKED", post)
        rel2 = Relationship(post, "TAGGED", topic)
        graph.create(rel)
        graph.create(rel2)

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

    def getQuestion(self, quer):
        whoAsked = "MATCH(n:User)-[:ASKED]->(m:Question) WHERE m.id = {quer} RETURN n.username"
        tagged = "MATCH(n:Topic)<-[:TAGGED]-(m:Question) WHERE m.id = {quer} RETURN n.topic"
        book = "match(u:User), (q:Question) WHERE u.username={user} AND q.id={title} RETURN EXISTS((u)-[:BOOKMARKED]-(q))"
        user = graph.run(whoAsked, quer=quer).evaluate()
        tag = graph.run(tagged, quer = quer).evaluate()
        bmrk = graph.run(book, user=self.username, title=quer).evaluate()
        quest = self.findByID(quer)
        return quest, user, tag, bmrk

    def getSearch(self, quer):
        tagged = "MATCH(n:Topic)<-[:TAGGED]-(m:Question) WHERE m.title = {quer} RETURN n.topic"
        res = "MATCH(n:Question) WHERE toLower(n.title) CONTAINS toLower({quer}) RETURN n ORDER BY n.date"
        tags = []
        ld = []
        c = 0
        for record in graph.run(res, quer=quer):
            a = [record['n']['title'], record['n']['text'], record['n']['id']]
            ld.append(a)
            tags.append(graph.run(tagged, quer = record['n']['title']).evaluate())
            c += 1
        return tags, ld, c

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
