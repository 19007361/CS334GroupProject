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
                title=title,
                text=text,
                date=date()
        )
        rel = Relationship(user, "ASKED", post)
        rel2 = Relationship(post, "TAGGED", topic)
        graph.create(rel)
        graph.create(rel2)

    def getPosts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT 5
        """
        return graph.run(query, username=self.username)

    def getQuestion(self, quer):
        whoAsked = "MATCH(n:User)-[:ASKED]->(m:Question) WHERE m.title = {quer} RETURN n.username"
        tagged = "MATCH(n:Topic)<-[:TAGGED]-(m:Question) WHERE m.title = {quer} RETURN n.topic"
        user = graph.run(whoAsked, quer=quer).evaluate()
        tag = graph.run(tagged, quer = quer).evaluate()
        quest = self.findT(quer)
        return quest, user, tag

    def getSearch(self, quer):
        tagged = "MATCH(n:Topic)<-[:TAGGED]-(m:Question) WHERE m.title = {quer} RETURN n.topic"
        res = "MATCH(n:Question) WHERE toLower(n.title) CONTAINS toLower({quer}) RETURN n ORDER BY n.date"
        tags = []
        ld = []
        c = 0
        for record in graph.run(res, quer=quer):
            a = [record['n']['title'], record['n']['text']]
            ld.append(a)
            tags.append(graph.run(tagged, quer = record['n']['title']).evaluate())
            c += 1
        return tags, ld, c


    def upvoteQuestion(self, qID):
        user = self.find()
        post = graph.find_one("Post", "id", qID)
        graph.create_unique(Relationship(user, "LIKE", post))

    # To get similar users use same procedure as getPosts
