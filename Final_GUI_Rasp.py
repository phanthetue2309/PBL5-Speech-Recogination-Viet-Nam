import os
import librosa
import socket
import numpy as np
import warnings
import serial
import pyaudio
import wave
import time

from keras.models import load_model
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy.io import wavfile

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# shape = 24000
shape = 31951
classes = ['dừng lại','quay phải','quay trái','sang phải','sang trái','đi lui','đi tới']
model=load_model('best_model_hdf5/best_model_5.hdf5')

# device's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

SEPARATOR = "<SEPARATOR>"
received_files = ""


class Ui_Dialog(object):

    def OpenServer(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.lineLocalhost.setText(local_ip)
        s = socket.socket()
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen(5)
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        client_socket, address = s.accept() 
        print(f"[+] {address} is connected.")
        received = client_socket.recv(BUFFER_SIZE).decode("utf-8")
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    break
                f.write(bytes_read)
        client_socket.close()
        # close the server socket
        s.close()
        print("Finish Receive")
        
    def Record_File(self,name_file="test.wav"):
        '''
        Hàm Ghi âm giọng nói. 
        '''
        form_1 = pyaudio.paInt16 # 16-bit resolution
        chans = 1 # 1 channel
        samp_rate = 44100 # 44.1kHz sampling rate
        chunk = 4096 # 2^12 samples for buffer
        record_secs = 4 # seconds to record

        dev_index = 0 # device index found by p.get_device_info_by_index(ii)
        wav_output_filename = name_file # name of .wav file

        audio = pyaudio.PyAudio() # create pyaudio instantiation

        # create pyaudio stream
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)

        frames = []
        
        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk)
            frames.append(data)
        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
    
    def GetFileFromRaspberry(self):
        self.lineFileReceived.setText("test.wav")

    def Calculate_Energy(self,data, frames,samplerate=44100):
        '''
        Hàm tính toán năng lượng 
        '''
        data0 = [i**2 for i in data] 
        E = np.empty(1, dtype=np.int64)
        samplein10 = int(samplerate * 0.01)
        for i in range(frames):
            c = np.empty(1, dtype=np.int64)
            for j in range(samplein10):
                c = np.append(c, data0[i * samplein10 + j])
            c = np.delete(c, 0) # xoa junk value
            d = np.sum(c)
            E = np.append(E, d)
        E = np.delete(E, 0) # xoa junk value 
        return E

    def Detect_Voice(self,E,data):
        '''
        Tìm ngưỡng năng lượng chuẩn bị
        '''
        nguong_E = 5*100000000 # 5x10^8 ngưỡng mặc định ứng với mic ghi âm
        maxE = max(E)
        if maxE < nguong_E : 
            self.labelStatus.setText("NO VOICE")
        else : 
            E = E / maxE  # chuẩn hóa về 0 -> 1 
            draw = []  # mảng đánh dấy vị trí bắt đầu và kết thúc của tiếng nói
            nguong_y = 0.06 # ngưỡng chọn 
            check = 0 # kiểm tra xem là vị trí bắt đầu hay kết thúc
            for m in range(0,len(E) - 3) : 
                if(E[m] > nguong_y and check==0) :
                    a = True
                    for i in range(m,m+3) :
                        if (E[i] < nguong_y) :
                            a = False
                            break
                    if (a == True) :
                        draw.append(m)
                        check = 1  # bắt đầu vào ngưỡng
                elif (E[m] < nguong_y and check==1) :
                    a=True
                    for i in range(m,m+3):
                        if (E[i] > nguong_y):
                            a=False
                            break
                    if(a==True):
                        draw.append(m-1)
                        check = 0   # kết thúc 1 chữ

            if (len(draw) >= 3 ): # nếu phát hiện được số lượng vị trí khung có tiếng nói thì thực thi
                self.labelStatus.setText("VOICE DETECT")            
                # self.predict(data[4000:28000]) 
                self.predict(data)
            else:
                self.labelStatus.setText("NO VOICE DETECT")

    def Action_Record(self) :
        self.labelStatus.repaint()
        self.labelStatus.setText("START RECORDING")
        QtCore.QCoreApplication.processEvents()

        self.Record_File()

        self.labelStatus.repaint()
        self.labelStatus.setText("FINISH RECORDING")
        QtCore.QCoreApplication.processEvents()

        time.sleep(1)
        name_file = "test.wav"
        samplerate, data1 = wavfile.read(name_file)
        data  = []
        if len(data1.shape) == 2:
            if data1.shape[1] !=  1 :
                for i in range(len(data1)):
                    data.append(data1[i][1])
        else : 
            data = data1
        frames = (float)((len(data) / samplerate)) 
        frames = (int)(frames*100)  

        #E = self.Calculate_Energy(data, frames)
        samples, sample_rate = librosa.load(name_file, sr = 44100)
        samples = librosa.resample(samples, sample_rate, 8000)
        #self.Detect_Voice(E,samples)
        # self.predict(samples[4000:28000])
        self.predict(samples)

    def predict(self,audio):
        prob=model.predict(audio.reshape(1,shape,1)) 
        print(prob[0])
        index=np.argmax(prob[0])
        
        self.lineFilePredict.setText(classes[index])
        print(classes[index])
        return classes[index]

    def PredictFile(self):       
        name_file = "test.wav"  
        samples, sample_rate = librosa.load(name_file, sr = 44100)
        samples = librosa.resample(samples, sample_rate, 8000)
        # file_predict = self.predict(samples[4000:28000])
        file_predict = self.predict(samples)
        self.lineFilePredict.setText(file_predict)   

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 500)
        self.ButtonServer = QtWidgets.QPushButton(Dialog)
        self.ButtonServer.setGeometry(QtCore.QRect(20, 240, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonServer.setFont(font)
        self.ButtonServer.setObjectName("ButtonServer")
        self.lineFileReceived = QtWidgets.QLineEdit(Dialog)
        self.lineFileReceived.setGeometry(QtCore.QRect(550, 240, 191, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineFileReceived.setFont(font)
        self.lineFileReceived.setObjectName("lineFileReceived")
        self.lineLocalhost = QtWidgets.QLineEdit(Dialog)
        self.lineLocalhost.setGeometry(QtCore.QRect(150, 240, 190, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineLocalhost.setFont(font)
        self.lineLocalhost.setObjectName("lineLocalhost")
        self.labelServer = QtWidgets.QLabel(Dialog)
        self.labelServer.setGeometry(QtCore.QRect(20, 190, 330, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelServer.setFont(font)
        self.labelServer.setObjectName("labelServer")
        self.ButtonPredict = QtWidgets.QPushButton(Dialog)
        self.ButtonPredict.setGeometry(QtCore.QRect(440, 330, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonPredict.setFont(font)
        self.ButtonPredict.setObjectName("ButtonPredict")
        self.lineFilePredict = QtWidgets.QLineEdit(Dialog)
        self.lineFilePredict.setGeometry(QtCore.QRect(550, 330, 190, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineFilePredict.setFont(font)
        self.lineFilePredict.setObjectName("lineFilePredict")
        self.labelFileReceived = QtWidgets.QLabel(Dialog)
        self.labelFileReceived.setGeometry(QtCore.QRect(550, 190, 140, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFileReceived.setFont(font)
        self.labelFileReceived.setObjectName("labelFileReceived")
        self.labelFilePredict = QtWidgets.QLabel(Dialog)
        self.labelFilePredict.setGeometry(QtCore.QRect(550, 290, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict.setFont(font)
        self.labelFilePredict.setObjectName("labelFilePredict")
        self.ButtonReceived = QtWidgets.QPushButton(Dialog)
        self.ButtonReceived.setGeometry(QtCore.QRect(440, 240, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonReceived.setFont(font)
        self.ButtonReceived.setObjectName("ButtonReceived")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 150, 551, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 380, 551, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.ButtonPredict_2 = QtWidgets.QPushButton(Dialog)
        self.ButtonPredict_2.setGeometry(QtCore.QRect(200, 440, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonPredict_2.setFont(font)
        self.ButtonPredict_2.setObjectName("ButtonPredict_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 20, 551, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.ButtonServer_2 = QtWidgets.QPushButton(Dialog)
        self.ButtonServer_2.setGeometry(QtCore.QRect(20, 70, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonServer_2.setFont(font)
        self.ButtonServer_2.setObjectName("ButtonServer_2")
        self.labelStatus = QtWidgets.QLabel(Dialog)
        self.labelStatus.setGeometry(QtCore.QRect(170, 70, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelStatus.setFont(font)
        self.labelStatus.setObjectName("labelStatus")

        self.ButtonServer_2.clicked.connect(self.Action_Record)
        self.ButtonPredict.clicked.connect(self.PredictFile)
        self.ButtonServer.clicked.connect(self.OpenServer)
        self.ButtonReceived.clicked.connect(self.GetFileFromRaspberry)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Speech Recogition"))
        self.ButtonServer.setText(_translate("Dialog", "Open Server"))
        self.labelServer.setText(_translate("Dialog", "Server Host ( Connect Raspberry ): "))
        self.ButtonPredict.setText(_translate("Dialog", "Predict File"))
        self.labelFileReceived.setText(_translate("Dialog", "File Received : "))
        self.labelFilePredict.setText(_translate("Dialog", "File After Predict :"))
        self.ButtonReceived.setText(_translate("Dialog", "Received File"))
        self.label.setText(_translate("Dialog", "CONNECT RASPBERRY AND PREDICT DATA RECEIVE"))
        self.label_2.setText(_translate("Dialog", "SEND DATA TO ARDUINO AND REMOTE THE CAR"))
        self.ButtonPredict_2.setText(_translate("Dialog", "SEND DATA"))
        self.label_3.setText(_translate("Dialog", "RECORD AND DETECT VOICE"))
        self.ButtonServer_2.setText(_translate("Dialog", "START"))
        self.labelStatus.setText(_translate("Dialog", "CLICK TO START RECORDING"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
