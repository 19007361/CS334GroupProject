from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid

graph = Graph()

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

    def getUser(self):
        user = graph.find_one("User", "Username", self.username)
        return user

    def addUser(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def checkPass(self, password):
        user = self.find()
        if user:
            return bcrypt.verify_password(password, user['password'])
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
        
