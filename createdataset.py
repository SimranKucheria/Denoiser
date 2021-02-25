import numpy as np 
import pandas as pd
import os 
import librosa
import tensorflow as tf
import warnings
warnings.filterwarnings("ignore")
import math
import pydub
from pydub import AudioSegment
from pydub.playback import play
import scipy
from sklearn.preprocessing import StandardScaler
import multiprocessing


train1=pd.read_csv('/media/sf_cv-corpus-6.1-2020-12-11/en/train.tsv', sep='\t')
train2=pd.read_csv('/media/sf_UrbanSound8K/metadata/UrbanSound8K.csv')

all1files=train1['path'].values
all1files = [os.path.join('/media/sf_cv-corpus-6.1-2020-12-11/en', 'clips', filename) for filename in all1files]
train1files = all1files[:-112900]
val1files = all1files[-112900:]

all2files=train2[['slice_file_name','fold']].values
all2files = [os.path.join('/media/sf_UrbanSound8K/audio', 'fold'+ str(filename[1]), str(filename[0])) for filename in all2files]
train2files = all2files[:-1747]
val2files = all2files[-1747:]

def _bytes_feature(value):
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy()  # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def processingparellel(filepath):
    num=filepath.split('_')
    num=num[-1]
    num=num[:-3]
    audio,sr=librosa.load(filepath,16000)  #Loads 16000 samples per second
    div_fac = 1 / np.max(np.abs(audio))    #For normalising audio
    audio = audio * div_fac / 3.0
    trimmed_audio = []
    indices = librosa.effects.split(audio, hop_length= 64, top_db=20)   #Removing silence
    for index in indices:
        trimmed_audio.extend(audio[index[0]: index[1]])		#Append non silent sections
    audio=np.array(trimmed_audio)
        
    noisefile =np.random.choice(train2files) #Select a random noise file

    noise_audio, sr = librosa.load(noisefile, 16000)   #Loads 16000 samples of noise file per second
    div_fac = 1 / np.max(np.abs(noise_audio))  / 3.0       #For normalising audio
    noise_audio = noise_audio * div_fac
    noisetrimmed_audio = []
    indices = librosa.effects.split(noise_audio, hop_length= 64, top_db=20)  #Removing silence
    for index in indices:
        noisetrimmed_audio.extend(noise_audio[index[0]: index[1]])	#Append non silent sections
    noise_audio=np.array(noisetrimmed_audio)

    audioduration = librosa.core.get_duration(audio, 16000)
    if audioduration>0.8:  						#Get a random 0.8 sec audio clip
        audioms = math.floor(audioduration * 16000)
        durms = math.floor(0.8 * 16000)
        idx = np.random.randint(0, audioms - durms)
        audio= audio[idx: idx + durms]
        
    if len(audio) >= len(noise_audio):
           while len(audio) >= len(noise_audio):
                noise_audio = np.append(noise_audio, noise_audio)	#If noise audio isnt enough loop it to make it greater than audio

    ind = np.random.randint(0, noise_audio.size - audio.size)
    noiseSegment = noise_audio[ind: ind + audio.size]			#Take a random noise segment similar in size to the audio clip
    audiop = np.sum(audio ** 2)
    noisep = np.sum(noiseSegment ** 2)
    noiseInput = audio + np.sqrt(audiop / noisep) * noiseSegment #Combining the 2 files to introduce noise in the audio

    noise_spectrogram =librosa.stft(noiseInput, n_fft=256, win_length=256, hop_length=64, window=scipy.signal.hamming(256, sym=False), center=True)  #Get Spectogram from audio
    noise_phase = np.angle(noise_spectrogram) #Used for scaling magnitude
    noise_magnitude = np.abs(noise_spectrogram) 

    clean_spectrogram = librosa.stft(audio, n_fft=256, win_length=256, hop_length=64, window=scipy.signal.hamming(256, sym=False), center=True) #Get Spectogram from audio
    clean_phase = np.angle(clean_spectrogram) #Used for scaling magnitude
    clean_magnitude = np.abs(clean_spectrogram)   
    if clean_phase.shape == noise_phase.shape:
            clean_magnitude =  clean_magnitude * np.cos(clean_phase - noise_phase) #To avoid extremities due to phase

    scaler = StandardScaler(copy=False, with_mean=True, with_std=True) 
    noise_magnitude = scaler.fit_transform(noise_magnitude) #Standardising features
    clean_magnitude = scaler.transform(clean_magnitude)
    

    noisySTFT = np.concatenate([noise_magnitude[:, 0:7], noise_magnitude], axis=1)
    stftSegments = np.zeros((129, 8, noisySTFT.shape[1] - 7 ))

    for index in range(noisySTFT.shape[1] - 7):
        stftSegments[:, :, index] = noisySTFT[:, index:index + 8]
    stftSegments = np.transpose(stftSegments, (2, 0, 1))
    clean_magnitude = np.transpose(clean_magnitude, (1, 0))
    noise_phase = np.transpose(noise_phase, (1, 0))

    stftSegments = np.expand_dims(stftSegments, axis=3)
    clean_magnitude = np.expand_dims(clean_magnitude, axis=2)
    tfrecord_filename = 'trainrecords' + num + 'tfrecords'
    writer = tf.io.TFRecordWriter(tfrecord_filename) #Write spectograms to file
    for x_, y_, p_ in zip(stftSegments, clean_magnitude, noise_phase):
        y_ = np.expand_dims(y_, 2)
        x_ = x_.astype(np.float32).tobytes()
        y_ = y_.astype(np.float32).tobytes()
        p_ = p_.astype(np.float32).tobytes()
        feat={
            "noise_stft_phase": _bytes_feature(p_),
            "noise_stft_mag_features": _bytes_feature(x_),
            "clean_stft_magnitude": _bytes_feature(y_)}
        example = tf.train.Example(features=tf.train.Features(feature=feat))
        writer.write(example.SerializeToString())
    writer.close()

p = multiprocessing.Pool(multiprocessing.cpu_count())
p.map(processingparellel,train1files)

//used same code with argument changes to create validation dataset
