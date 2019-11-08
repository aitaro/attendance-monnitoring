from flask import Flask
from flask import request
from main import main
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def root():
    return main(request)