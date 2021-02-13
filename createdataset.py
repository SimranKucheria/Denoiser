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

for filepath in train1files:
    print(filepath)
    audio,sr=librosa.load(filepath,16000)  #Loads 16000 samples per second
    div_fac = 1 / np.max(np.abs(audio))    #For normalising audio
    audio = audio * div_fac / 3.0
    print( np.max(np.abs(audio)))
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

    #Next couple of lines are for testing if audio gets merged properly 

    #audio_segment = pydub.AudioSegment(
    #audio.tobytes(), 
    #frame_rate=16000,
    #sample_width=audio.dtype.itemsize, 
    #channels=1
    #)
    #play(audio_segment)
    #audio_segment = pydub.AudioSegment(
    #noiseSegment.tobytes(), 
    #frame_rate=16000,
    #sample_width=noiseSegment.dtype.itemsize, 
    #channels=1
    #)
    #play(audio_segment)
    #audio_segment = pydub.AudioSegment(
    #noiseInput.tobytes(), 
    #frame_rate=16000,
    #sample_width=noiseInput.dtype.itemsize, 
    #channels=1
    #)
    #play(audio_segment)
