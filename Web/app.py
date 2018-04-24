from flask import *
from py2neo import *


app = Flask(__WhoCares__)

if __WhoCares__ == '__main__':
    app.run(debug=True)
