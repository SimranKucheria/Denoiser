from flask import Flask, render_template, redirect, session
from functools import wraps
from models import User
import db

app = Flask(__name__)
app.secret_key = "secret"


def login_required(f):
    @wraps(f)
    def wrap(*arg, **kwargs):
        if 'logged_in' in session:
            return f(*arg, **kwargs)
        else:
            return redirect('/')

    return wrap


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    return User().signup()


@app.route('/user/signout', methods=['GET', 'POST'])
def signout():
    return User().signout()


@app.route('/user/login', methods=['POST'])
def login():
    return User().login()


@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')


# if __name__ == '__main__':
#     app.run(debug=True)
