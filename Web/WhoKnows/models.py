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
        post = Node(
                "Post",
                id=str(uuid.uuid4()),
                title=title,
                text=text,
                timestamp=timestamp(),
                date=date()
        )
        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)


    def getPosts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT 5
        """
        return graph.run(query, username=self.username)

    def upvoteQuestion(self, qID):
        user = self.find()
        post = graph.find_one("Post", "id", qID)
        graph.create_unique(Relationship(user, "LIKE", post))

    # To get similar users use same procedure as getPosts
