from flask import Flask, render_template, redirect, session, request
from functools import wraps
from models import User
import db
from denoiser import getcleanaudio

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
    
@app.route('/denoiser',methods=['GET','POST','PUT'])
@login_required
def denoiser():
    #if request.method == 'POST':
     #   audio = request.files['audio_data']
      #  return render_template('denoiseroutput.html', input=getcleanaudio(model=model, inputaudio=audio))
    # Send template information to index.html
    #return render_template('model.html')
    with open('/tmp/audio.wav', 'wb') as f:
        f.write(request.data)
    proc = run(['ffprobe', '-of', 'default=noprint_wrappers=1', '/tmp/audio.wav'], text=True, stderr=PIPE)
    return proc.stderr


from keras.models import load_model
import tensorflow as tf
import warnings
warnings.filterwarnings('ignore')

def load_keras_model():
    global model
    model = load_model('../model3.h5')

if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))
    #load_keras_model()
    app.run(host="0.0.0.0", port=5000)
