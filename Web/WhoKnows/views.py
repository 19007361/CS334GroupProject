from flask import  Flask, render_template, flash, redirect, url_for, session, request, logging
from py2neo import *


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/p/')
def profile():
    return render_template('profile.html')
