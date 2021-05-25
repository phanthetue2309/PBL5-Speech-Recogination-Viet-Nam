import os
import librosa
import numpy as np
from keras.models import load_model
model=load_model('best_model.hdf5')
classes = ['quay trái', 'quay phải', 'sang phải', 'sang trái', "đi tới", "đi lui"]

shape = 20800
def predict(audio):
    prob=model.predict(audio.reshape(1,shape,1))  
    index=np.argmax(prob[0])
    return classes[index]


filepath='input/voice-commands/test'
waves = [f for f in os.listdir(filepath + '/') if f.endswith('.wav')]
for wav in waves:
    samples, sample_rate = librosa.load(filepath + '/' + wav, sr = 44100)
    samples = librosa.resample(samples, sample_rate, 16000) # phải resample về lại mẫu đã train 
    file_predict = predict(samples[0:shape])
    print(wav + " : " + file_predict)
