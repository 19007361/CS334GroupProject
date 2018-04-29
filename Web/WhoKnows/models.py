from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid

graph = Graph()

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
