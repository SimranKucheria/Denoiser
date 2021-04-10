from keras.models import load_model
import tensorflow as tf
import librosa
import IPython.display as ipd
import librosa.display
import scipy
import numpy as np 
import pandas as pd 
import os
import speech_recognition

def revert_features_to_audio(features, phase, cleanMean, cleanStd):
    features = cleanStd * features + cleanMean #Remove standardisation

    phase = np.transpose(phase, (1, 0))
    features = np.squeeze(features)

    features = features * np.exp(1j * phase)  #Removes the abs()

    features = np.transpose(features, (1, 0))
    return librosa.istft(features,win_length=256, hop_length=64, window=scipy.signal.hamming(256, sym=False), center=True)
    
def getcleanaudio(model,inputaudio):
	noise_stft_features = librosa.stft(inputaudio, n_fft=256, win_length=256, hop_length=64, window=scipy.signal.hamming(256, sym=False), center=True) #Get Spectogram from audio
	noisyPhase = np.angle(noise_stft_features)

	noise_stft_features = np.abs(noise_stft_features)

	mean = np.mean(noise_stft_features)
	std = np.std(noise_stft_features)
	noise_stft_features = (noise_stft_features - mean) / std #Standardise

	noisySTFT = np.concatenate([noise_stft_features[:,0:7], noise_stft_features], axis=1)
	stftSegments = np.zeros((129, 8, noisySTFT.shape[1] - 7 ))

	for index in range(noisySTFT.shape[1] - 7):
		stftSegments[:, :, index] = noisySTFT[:, index:index + 8]
	predictors=stftSegments
	predictors = np.reshape(predictors, (predictors.shape[0], predictors.shape[1], 1, predictors.shape[2]))
	predictors = np.transpose(predictors, (3, 0, 1, 2)).astype(np.float32)
	#Transorm into form to input to model
	Pred = model.predict(predictors)
	outputaud=revert_features_to_audio(Pred, noisyPhase, mean, std)
	# Use speech recognition outputtext=
	return outputaud
	
	
	    
