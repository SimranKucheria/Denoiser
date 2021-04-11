from flask import Flask, render_template, redirect, session, request

app = Flask(__name__, template_folder='templates')
app.secret_key = "secret"


@app.route('/')
def home():
    return render_template('news.html')
