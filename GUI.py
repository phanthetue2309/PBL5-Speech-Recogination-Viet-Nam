from PyQt5 import QtCore, QtGui, QtWidgets
import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import librosa
import socket
import numpy as np
import librosa
import warnings
warnings.filterwarnings("ignore")

shape = 50
classes = ['dừng lại', 'quay phải', 'quay trái', 'sang phải', 'sang trái', 'đi lui', 'đi tới']

from keras.callbacks import  ModelCheckpoint

model=tf.keras.models.load_model('best_model.h5')
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
mc = ModelCheckpoint('best_model.h5', monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')


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
        
        
    def GetFileFromRaspberry(self):
        self.lineFileReceived.setText("test.wav")
        

    def predict(self,audio):
        prob=model.predict(audio.reshape(1,shape,1))  
        index=np.argmax(prob[0])
        return classes[index]

    def PredictFile(self):         

        wav  = "test.wav"    
        #samples, sample_rate = librosa.load(wav, sr = 44100)
        #samples = librosa.resample(samples, sample_rate, 16000) # phải resample về lại mẫu đã train 
        with open('text.txt') as f:
            data = []
            one_line = ''
            for line in f:   
                line = line.replace('[', '')
                line = line.replace(']', '')
                one_line += line
                
            data = [float(item) for item in one_line.split()]    
        samples = np.array(data)
        file_predict = self.predict(samples[0:shape])
        self.lineFilePredict.setText(file_predict)   

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(715, 480)
        self.ButtonServer = QtWidgets.QPushButton(Dialog)
        self.ButtonServer.setGeometry(QtCore.QRect(30, 280, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonServer.setFont(font)
        self.ButtonServer.setObjectName("ButtonServer")
        self.lineFileReceived = QtWidgets.QLineEdit(Dialog)
        self.lineFileReceived.setGeometry(QtCore.QRect(470, 280, 191, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineFileReceived.setFont(font)
        self.lineFileReceived.setObjectName("lineFileReceived")
        self.lineLocalhost = QtWidgets.QLineEdit(Dialog)
        self.lineLocalhost.setGeometry(QtCore.QRect(140, 280, 190, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineLocalhost.setFont(font)
        self.lineLocalhost.setObjectName("lineLocalhost")
        self.labelServer = QtWidgets.QLabel(Dialog)
        self.labelServer.setGeometry(QtCore.QRect(90, 240, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelServer.setFont(font)
        self.labelServer.setObjectName("labelServer")
        self.ButtonPredict = QtWidgets.QPushButton(Dialog)
        self.ButtonPredict.setGeometry(QtCore.QRect(360, 380, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonPredict.setFont(font)
        self.ButtonPredict.setObjectName("ButtonPredict")
        self.lineFilePredict = QtWidgets.QLineEdit(Dialog)
        self.lineFilePredict.setGeometry(QtCore.QRect(470, 380, 190, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineFilePredict.setFont(font)
        self.lineFilePredict.setObjectName("lineFilePredict")
        self.labelFileReceived = QtWidgets.QLabel(Dialog)
        self.labelFileReceived.setGeometry(QtCore.QRect(470, 240, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFileReceived.setFont(font)
        self.labelFileReceived.setObjectName("labelFileReceived")
        self.labelFilePredict = QtWidgets.QLabel(Dialog)
        self.labelFilePredict.setGeometry(QtCore.QRect(470, 340, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict.setFont(font)
        self.labelFilePredict.setObjectName("labelFilePredict")
        self.ButtonReceived = QtWidgets.QPushButton(Dialog)
        self.ButtonReceived.setGeometry(QtCore.QRect(360, 280, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonReceived.setFont(font)
        self.ButtonReceived.setObjectName("ButtonReceived")

        self.ButtonPredict.clicked.connect(self.PredictFile)
        self.ButtonServer.clicked.connect(self.OpenServer)
        self.ButtonReceived.clicked.connect(self.GetFileFromRaspberry)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Speech Recogition"))
        self.ButtonServer.setText(_translate("Dialog", "Open Server"))
        self.labelServer.setText(_translate("Dialog", "Server Host : "))
        self.ButtonPredict.setText(_translate("Dialog", "Predict File"))
        self.labelFileReceived.setText(_translate("Dialog", "File Received : "))
        self.labelFilePredict.setText(_translate("Dialog", "File After Predict :"))
        self.ButtonReceived.setText(_translate("Dialog", "Received File"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
