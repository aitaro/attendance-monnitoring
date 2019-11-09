from flask import Flask
from flask import request
from main import main
from flask import jsonify
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def root():
    return main(request)

@app.route('/health-check', methods=["GET", "POST"])
def health_check():
    return 'ok'