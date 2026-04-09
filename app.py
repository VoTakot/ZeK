import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


@app.route('/')
def index():
    return render_template('base.html', title='ZeK')


if __name__ == '__main__':
    app.run('127.0.0.1',    8080)