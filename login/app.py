import warnings
#import tensorflow as tf
#from keras.models import load_model
from flask import Flask, render_template, redirect, session, request
from functools import wraps
from models import User
#from models import BlogArticleForm, Article
import db
#from denoiser import getcleanaudio
from subprocess import run, PIPE


app = Flask(__name__)
app.secret_key = "secret"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


warnings.filterwarnings('ignore')


#def load_keras_model():
 #   global model
  #  print("Model Loaded")
   # model = load_model('../model3.h5')


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


@app.route('/recorder')
def recorder():
    return render_template('recorder.html')


@app.route('/blog/write')
def blog_form():
    form = BlogArticleForm()
    return render_template('add_article.html', form=form)


@app.route('/write_article', methods=['POST'])
def add_article():
    return Article().create_article(session['user'])


@app.route('/blog/articles')
def articles():
    articles = Article().get_articles()
    return render_template('articles.html', articles=articles)


@app.route('/blog/articles/<string:id>')
def article(id):
    article = Article().get_article(id)
    print(article)
    return render_template('article.html', article=article)


#@app.route('/audio', methods=['POST', 'GET'])
#def audio():
 #   if request.method == 'POST':
  #      with open('/tmp/audio.wav', 'wb') as f:
   #         f.write(request.data)
    #    f.close()
    #    x = getcleanaudio(model=model, filename='/tmp/audio.wav')
    #print(x)
    #return x


@app.route('/play')
def play():
    return render_template('denoiseroutput.html')


@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/news')
@login_required
def news():
    return render_template('news.html')


#if __name__ == "__main__":
#    print(("* Loading Keras model and Flask starting server..."
#          "please wait until server has fully started"))
#    load_keras_model()
#    app.run(host="127.0.0.1", port=5000, debug=True)
