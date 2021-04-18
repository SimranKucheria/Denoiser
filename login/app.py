import warnings
import tensorflow as tf
from keras.models import load_model
from flask import Flask, render_template, redirect, session, request, flash, jsonify, url_for
from functools import wraps
from models import BlogArticleForm, Article, EmailForm, PasswordForm, ContactUsForm, Comment, CommentForm, User
import db
from denoiser import getcleanaudio
from subprocess import run, PIPE
from flask_json import json_response
from flask_mail import Mail, Message
from itsdangerous.url_safe import URLSafeSerializer
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = "secret"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['JSON_ADD_STATUS'] = False
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'canyouhearmeservice@gmail.com'
app.config['MAIL_PASSWORD'] = 'dummypassword'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'canyouhearmeservice@gmail.com'

mail = Mail(app)

warnings.filterwarnings('ignore')


def load_keras_model():
    global model
    print("Model Loaded")
    model = load_model('../FinalModel.h5')


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
    #if 'logged_in' in session:
     #   return redirect('/dashboard/')
    return render_template('dashboard.html')
    
@app.route('/gettingstarted')
def getstarted():
	return render_template('home.html')


@app.route('/forgotpassword', methods=["GET", "POST"])
def forgotpassword():
    form = EmailForm()
    if request.method == 'POST':
        print(form.email.data)
        if db.db.users.find_one({'Email': 'simran.kucheria@gmail.com'}):
            print("Found")
        user = db.db.users.find_one({'Email': form.email.data})
        if user:
            s = URLSafeSerializer("secret-key")
            key = s.dumps(user['Email'])
            url = url_for('reset', token=key, _external=True)
            msg = Message('Password Change Request',
                          recipients=[user['Email']])
            msg.html = render_template(
                '/reset-email.html', username=user['Firstname'], link=url)
            mail.send(msg)
            return render_template('home.html')
        else:
            return jsonify({"error": "Email ID not found"}), 400

    return render_template('forgotpassword.html', form=form)


@app.route('/reset/<token>', methods=["GET", "POST"])
def reset(token):
    try:
        s = URLSafeSerializer("secret-key")
        email = s.loads(token)
        print("Here")
    except:
        return jsonify({"error": "Invalid Token"}), 400

    form = PasswordForm()

    if form.validate_on_submit():
        user = db.db.users.find_one(request.form.get('email'))

        if user:
            print(user['Email'])
            find = {"_id": user['_id']}
            pw = pbkdf2_sha256.encrypt(form.password.data)
            newval = {"$set": {"Password": pw}}
            db.db.users.update_one(find, newval)
            return redirect('/')

    return render_template('resettoken.html', form=form, token=token)


@app.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContactUsForm()
    if request.method == 'POST':

        msg = Message(form.subject.data, recipients=[
                      'canyouhearmeservice@gmail.com'])
        msg.html = render_template(
            '/contact-email.html', name=form.name.data, email=form.email.data, message=form.message.data)
        mail.send(msg)
        return render_template('home.html')
    return render_template('contact.html', form=form)


@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    return User().signup()


@app.route('/user/signout', methods=['GET', 'POST'])
def signout():
    return User().signout()


@app.route('/user/login', methods=['POST'])
def login():
    return User().login()


@app.route('/recorder')
@login_required
def recorder():
    return render_template('recorder.html')


@app.route('/blog/write')
@login_required
def blog_form():
    form = BlogArticleForm()
    return render_template('add_article.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/write_article', methods=['POST'])
@login_required
def add_article():
    return Article().create_article(session['user'])


@app.route('/write_comment/<string:id>', methods=['POST'])
@login_required
def add_comment(id):
    article = db.db.articles.find_one(id)
    return Comment().create_comment(session['user'], article)


@app.route('/delete_article/<string:id>', methods=['POST'])
@login_required
def delete_article(id):
    article = db.db.articles.find_one(id)
    user = session['user']
    if user['_id'] == article['user_id']:
        db.db.articles.delete_one({"_id": id})
        flash("Deleted article: "+article['title']+" successfully")
        return redirect('/dashboard/')
    else:
        flash("Could not delete article")
        return redirect('/dashboard/')


@app.route('/blog/user_articles/<string:id>', methods=['GET'])
@login_required
def get_user_articles(id):
    articles = Article().get_user_articles(id, session['user'])
    return render_template('user_articles.html', articles=articles)


@app.route('/blog/articles')
@login_required
def articles():
    articles = Article().get_articles()
    return render_template('articles.html', articles=articles)


@app.route('/blog/articles/<string:id>')
@login_required
def article(id):
    article = Article().get_article(id)
    user = session['user']
    comment_form = CommentForm()
    comments = Comment().get_comments(article)
    return render_template('article.html', article=article, user=user, comment_form=comment_form, comments=comments)


@app.route('/audio', methods=['POST', 'GET'])
def audio():
    if request.method == 'POST':
        with open('/tmp/audio.wav', 'wb') as f:
            f.write(request.data)
        f.close()
        x, y = getcleanaudio(model=model, filename='/tmp/audio.wav')
    print(x)
    return json_response(text=x, name=y)


@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/news')
@login_required
def news():
    return render_template('news.html')


if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))
    load_keras_model()
    app.run(host="127.0.0.1", port=5000)
