# import os
# import librosa
# import numpy as np
# import socket
# from keras.models import load_model
# model=load_model('best_model.hdf5')
# classes = ['quay trái', 'quay phải', 'sang phải', 'sang trái', "đi tới", "đi lui"]
# shape = 20800

#     def OpenServer(self):
#         hostname = socket.gethostname()
#         local_ip = socket.gethostbyname(hostname)
#         self.lineLocalhost.setText(local_ip)
    
#     def predict(self,audio):
#         prob=model.predict(audio.reshape(1,shape,1))  
#         index=np.argmax(prob[0])
#         return classes[index]

#     def PredictFile(self):
#         filepath='input/voice-commands/test_app'
#         waves = [f for f in os.listdir(filepath + '/') if f.endswith('.wav')]
#         for wav in waves:
#             samples, sample_rate = librosa.load(filepath + '/' + wav, sr = 44100)
#             samples = librosa.resample(samples, sample_rate, 16000) # phải resample về lại mẫu đã train 
#             file_predict = self.predict(samples[0:shape])
#             print(wav + " : " + file_predict)
#             self.lineFilePredict.setText(file_predict)

# this will be in the last of def setupUI 
# self.ButtonPredict.clicked.connect(self.PredictFile)
# self.ButtonServer.clicked.connect(self.OpenServer)