import os
import librosa
import numpy as np
import warnings
import serial
import pyaudio
import wave
import time

from keras.models import load_model
from scipy.io import wavfile
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMovie

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
shape = 31951
classes = ['dừng lại', 'quay phải', 'quay trái',
           'sang phải', 'sang trái', 'đi lui', 'đi tới']
model = load_model('best_model_hdf5/best_model_5.hdf5')


class Ui_Dialog(object):
    def Record_File(self, name_file="test.wav"):
        '''
        Hàm Ghi âm giọng nói. 
        '''
        form_1 = pyaudio.paInt16  # 16-bit resolution
        chans = 1  # 1 channel
        samp_rate = 44100  # 44.1kHz sampling rate
        chunk = 4096  # 2^12 samples for buffer
        record_secs = 4  # seconds to record

        dev_index = 0  # device index found by p.get_device_info_by_index(ii)
        wav_output_filename = name_file  # name of .wav file

        audio = pyaudio.PyAudio()  # create pyaudio instantiation

        # create pyaudio stream
        stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                            input_device_index=dev_index, input=True,
                            frames_per_buffer=chunk)

        frames = []

        for ii in range(0, int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()

        wavefile = wave.open(wav_output_filename, 'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

    def Calculate_Energy(self, data, frames, samplerate=44100):
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
            c = np.delete(c, 0)  # xoa junk value
            d = np.sum(c)
            E = np.append(E, d)
        E = np.delete(E, 0)  # xoa junk value
        return E

    def Detect_Voice(self, E):
        '''
        Tìm ngưỡng năng lượng chuẩn bị
        '''
        maxE = max(E)
        E = E / maxE  # chuẩn hóa về 0 -> 1
        draw = []  # mảng đánh dấy vị trí bắt đầu và kết thúc của tiếng nói
        nguong_y = 0.05  # ngưỡng chọn
        check = 0  # kiểm tra xem là vị trí bắt đầu hay kết thúc
        for m in range(0, len(E) - 3):
            if(E[m] > nguong_y and check == 0):
                a = True
                for i in range(m, m+3):
                    if (E[i] < nguong_y):
                        a = False
                        break
                if (a == True):
                    draw.append(m)
                    check = 1  # bắt đầu vào ngưỡng
            elif (E[m] < nguong_y and check == 1):
                a = True
                for i in range(m, m+3):
                    if (E[i] > nguong_y):
                        a = False
                        break
                if(a == True):
                    draw.append(m-1)
                    check = 0   # kết thúc 1 chữ

        # nếu phát hiện được số lượng vị trí khung có tiếng nói thì thực thi
        if (len(draw) >= 2 and len(draw) <= 4):
            self.labelStatus.setText("VOICE DETECT")
            self.PredictFile()
        elif (len(draw) > 4):
            self.labelStatus.setText("NO COMMAND DETECT")
            QtCore.QCoreApplication.processEvents()
            self.lineFilePredict.setText("")
            QtCore.QCoreApplication.processEvents()
            self.Image.setPixmap(QtGui.QPixmap(
                "advantages-of-speech-recognition.jpg"))
            QtCore.QCoreApplication.processEvents()
        else:
            self.labelStatus.setText("NO VOICE DETECT")
            QtCore.QCoreApplication.processEvents()
            self.lineFilePredict.setText("")
            QtCore.QCoreApplication.processEvents()
            self.Image.setPixmap(QtGui.QPixmap(
                "advantages-of-speech-recognition.jpg"))
            QtCore.QCoreApplication.processEvents()

    def Action_Record(self):
        self.btnStartRecord.setEnabled(False)
        self.labelStatus.repaint()
        self.labelStatus.setText("START RECORDING")
        QtCore.QCoreApplication.processEvents()

        self.Record_File()

        self.labelStatus.repaint()
        self.labelStatus.setText("FINISH RECORDING")
        QtCore.QCoreApplication.processEvents()

        time.sleep(1)
        name_file = "test.wav"
        samplerate, data = wavfile.read(name_file)
        frames = (float)((len(data) / samplerate))
        frames = (int)(frames*100)
        E = self.Calculate_Energy(data, frames)
        self.Detect_Voice(E)
        self.btnStartRecord.setEnabled(True)

    def predict(self, audio):
        prob = model.predict(audio.reshape(1, shape, 1))
        print(prob[0])
        if np.argmax(prob[0]) < 0.7:
            index = 10
            self.lineFilePredict.setText("NO COMMAND DETECT")
            return index
        index = np.argmax(prob[0])
        self.lineFilePredict.setText(classes[index])
        return index

    def PredictFile(self):
        name_file = "test.wav"
        samples, sample_rate = librosa.load(name_file, sr=44100)
        samples = librosa.resample(samples, sample_rate, 8000)
        index = self.predict(samples)

        if index == 6:
            self.movie = QMovie("di_toi.gif")
            self.ImageDraw.setMovie(self.movie)
            self.movie.start()
        elif index == 5:
            self.movie = QMovie("di_lui.gif")
            self.ImageDraw.setMovie(self.movie)
            self.movie.start()
        elif index == 1:
            self.movie = QMovie("quay_phai.gif")
            self.ImageDraw.setMovie(self.movie)
            self.movie.start()
        elif index == 2:
            self.movie = QMovie("quay_trai.gif")
            self.ImageDraw.setMovie(self.movie)
            self.movie.start()
        elif index == 3:
            self.movie = QMovie("sang_phai.gif")
            self.ImageDraw.setMovie(self.movie)
            self.movie.start()
        elif index == 4:
            self.movie = QMovie("sang_trai.gif")
            self.ImageDraw.setMovie(self.movie)
            self.movie.start()
        elif index == 0:
            self.ImageDraw.setPixmap(QtGui.QPixmap("dung_lai.png"))
        else:
            QtCore.QCoreApplication.processEvents()
            self.Image.setPixmap(QtGui.QPixmap(
                "advantages-of-speech-recognition.jpg"))
            QtCore.QCoreApplication.processEvents()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.resize(1300, 760)
        Dialog.setFixedSize(1300, 760)
        Dialog.setAcceptDrops(False)
        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.jpg"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setAutoFillBackground(False)
        self.ButtonPredict = QtWidgets.QPushButton(Dialog)
        self.ButtonPredict.setEnabled(True)
        self.ButtonPredict.setGeometry(QtCore.QRect(330, 410, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ButtonPredict.setFont(font)
        self.ButtonPredict.setObjectName("ButtonPredict")
        self.lineFilePredict = QtWidgets.QLineEdit(Dialog)
        self.lineFilePredict.setGeometry(QtCore.QRect(440, 410, 190, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineFilePredict.setFont(font)
        self.lineFilePredict.setObjectName("lineFilePredict")
        self.labelFilePredict = QtWidgets.QLabel(Dialog)
        self.labelFilePredict.setGeometry(QtCore.QRect(450, 360, 181, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict.setFont(font)
        self.labelFilePredict.setObjectName("labelFilePredict")
        self.labelSendArduino = QtWidgets.QLabel(Dialog)
        self.labelSendArduino.setGeometry(QtCore.QRect(20, 490, 301, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.labelSendArduino.setFont(font)
        self.labelSendArduino.setObjectName("labelSendArduino")
        self.btnSendData = QtWidgets.QPushButton(Dialog)
        self.btnSendData.setGeometry(QtCore.QRect(120, 540, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnSendData.setFont(font)
        self.btnSendData.setDefault(False)
        self.btnSendData.setFlat(False)
        self.btnSendData.setObjectName("btnSendData")
        self.labelRecord = QtWidgets.QLabel(Dialog)
        self.labelRecord.setGeometry(QtCore.QRect(20, 360, 120, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelRecord.setFont(font)
        self.labelRecord.setObjectName("labelRecord")
        self.btnStartRecord = QtWidgets.QPushButton(Dialog)
        self.btnStartRecord.setGeometry(QtCore.QRect(20, 410, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnStartRecord.setFont(font)
        self.btnStartRecord.setAutoDefault(True)
        self.btnStartRecord.setFlat(False)
        self.btnStartRecord.setObjectName("btnStartRecord")
        self.labelStatus = QtWidgets.QLabel(Dialog)
        self.labelStatus.setGeometry(QtCore.QRect(130, 410, 200, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelStatus.setFont(font)
        self.labelStatus.setObjectName("labelStatus")
        self.Image = QtWidgets.QLabel(Dialog)
        self.Image.setGeometry(QtCore.QRect(0, 0, 1300, 360))
        self.Image.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Image.setText("")
        self.Image.setPixmap(QtGui.QPixmap(
            "advantages-of-speech-recognition.jpg"))
        self.Image.setScaledContents(True)
        self.Image.setObjectName("Image")
        self.ImageDraw = QtWidgets.QLabel(Dialog)
        self.ImageDraw.setGeometry(QtCore.QRect(330, 500, 301, 181))
        self.ImageDraw.setText("")
        self.ImageDraw.setPixmap(QtGui.QPixmap("Full_Action.png"))
        self.ImageDraw.setScaledContents(True)
        self.ImageDraw.setObjectName("ImageDraw")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(650, 370, 2, 350))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(48)
        self.line.setFont(font)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.labelFilePredict_2 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_2.setGeometry(QtCore.QRect(670, 360, 140, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_2.setFont(font)
        self.labelFilePredict_2.setObjectName("labelFilePredict_2")
        self.labelFilePredict_3 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_3.setGeometry(QtCore.QRect(670, 400, 100, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_3.setFont(font)
        self.labelFilePredict_3.setObjectName("labelFilePredict_3")
        self.labelFilePredict_4 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_4.setGeometry(QtCore.QRect(670, 480, 100, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_4.setFont(font)
        self.labelFilePredict_4.setObjectName("labelFilePredict_4")
        self.labelFilePredict_5 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_5.setGeometry(QtCore.QRect(670, 560, 100, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_5.setFont(font)
        self.labelFilePredict_5.setObjectName("labelFilePredict_5")
        self.labelFilePredict_6 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_6.setGeometry(QtCore.QRect(820, 650, 100, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_6.setFont(font)
        self.labelFilePredict_6.setObjectName("labelFilePredict_6")
        self.labelFilePredict_7 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_7.setGeometry(QtCore.QRect(960, 400, 100, 50))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_7.setFont(font)
        self.labelFilePredict_7.setObjectName("labelFilePredict_7")
        self.labelFilePredict_8 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_8.setGeometry(QtCore.QRect(960, 480, 100, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_8.setFont(font)
        self.labelFilePredict_8.setObjectName("labelFilePredict_8")
        self.labelFilePredict_9 = QtWidgets.QLabel(Dialog)
        self.labelFilePredict_9.setGeometry(QtCore.QRect(960, 560, 100, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFilePredict_9.setFont(font)
        self.labelFilePredict_9.setObjectName("labelFilePredict_9")
        # di toi
        self.ditoiImage = QtWidgets.QLabel(Dialog)
        self.ditoiImage.setGeometry(QtCore.QRect(780, 400, 160, 80))
        self.ditoiImage.setText("")
        self.ditoiImage.setScaledContents(True)
        self.ditoiImage.setObjectName("ditoiImage")
        self.ditoiImage.setPixmap(QtGui.QPixmap("di_toi.png"))
        # sang phai
        self.sangphaiImage = QtWidgets.QLabel(Dialog)
        self.sangphaiImage.setGeometry(QtCore.QRect(780, 480, 160, 80))
        self.sangphaiImage.setText("")
        self.sangphaiImage.setScaledContents(True)
        self.sangphaiImage.setObjectName("sangphaiImage")
        self.sangphaiImage.setPixmap(QtGui.QPixmap("sang_phai.png"))
        # quay phai
        self.quayphaiImage = QtWidgets.QLabel(Dialog)
        self.quayphaiImage.setGeometry(QtCore.QRect(780, 560, 160, 80))
        self.quayphaiImage.setText("")
        self.quayphaiImage.setScaledContents(True)
        self.quayphaiImage.setObjectName("quayphaiImage")
        self.quayphaiImage.setPixmap(QtGui.QPixmap("quay_phai_01.png"))
        # dung lai
        self.dunglaiImage = QtWidgets.QLabel(Dialog)
        self.dunglaiImage.setGeometry(QtCore.QRect(920, 650, 160, 80))
        self.dunglaiImage.setText("")
        self.dunglaiImage.setScaledContents(True)
        self.dunglaiImage.setObjectName("dunglaiImage")
        self.dunglaiImage.setPixmap(QtGui.QPixmap("dung_lai.png"))
        # di lui
        self.diluiImage = QtWidgets.QLabel(Dialog)
        self.diluiImage.setGeometry(QtCore.QRect(1080, 400, 160, 80))
        self.diluiImage.setText("")
        self.diluiImage.setScaledContents(True)
        self.diluiImage.setObjectName("diluiImage")
        self.diluiImage.setPixmap(QtGui.QPixmap("di_lui.png"))
        # quay trai
        self.quaytraiImage = QtWidgets.QLabel(Dialog)
        self.quaytraiImage.setGeometry(QtCore.QRect(1080, 560, 160, 80))
        self.quaytraiImage.setText("")
        self.quaytraiImage.setScaledContents(True)
        self.quaytraiImage.setObjectName("quaytraiImage")
        self.quaytraiImage.setPixmap(QtGui.QPixmap("quay_trai_01.png"))
        # sang trai
        self.sangtraiImage = QtWidgets.QLabel(Dialog)
        self.sangtraiImage.setGeometry(QtCore.QRect(1080, 480, 160, 80))
        self.sangtraiImage.setText("")
        self.sangtraiImage.setScaledContents(True)
        self.sangtraiImage.setObjectName("sangtraiImage")
        self.sangtraiImage.setPixmap(QtGui.QPixmap("sang_trai.png"))
        # end of command
        # add action to button
        self.btnStartRecord.clicked.connect(self.Action_Record)
        self.ButtonPredict.clicked.connect(self.PredictFile)
        # end
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Speech Recogition"))
        self.ButtonPredict.setText(_translate("Dialog", "PREDICT"))
        self.labelFilePredict.setText(_translate("Dialog", "COMMAND PREDICT"))
        self.labelSendArduino.setText(_translate(
            "Dialog", "SEND COMMAND TO ARDUINO"))
        self.btnSendData.setText(_translate("Dialog", "SEND DATA"))
        self.labelRecord.setText(_translate("Dialog", "RECORDING"))
        self.btnStartRecord.setText(_translate("Dialog", "START"))
        self.labelStatus.setText(_translate("Dialog", "Nothing"))
        self.labelFilePredict_2.setText(_translate("Dialog", "LIST COMMAND"))
        self.labelFilePredict_3.setText(_translate("Dialog", "đi tới"))
        self.labelFilePredict_4.setText(_translate("Dialog", "sang phải"))
        self.labelFilePredict_5.setText(_translate("Dialog", "quay phải"))
        self.labelFilePredict_6.setText(_translate("Dialog", "dừng lại"))
        self.labelFilePredict_7.setText(_translate("Dialog", "đi lui"))
        self.labelFilePredict_8.setText(_translate("Dialog", "sang trái"))
        self.labelFilePredict_9.setText(_translate("Dialog", "quay trái"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
