import pyaudio
import wave
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np


def getaudiodevices():
    '''
    Kiểm tra thông tin thiết bị của micro usb
    '''
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i).get('name'))


# getaudiodevices()
name_file = "test.wav"


def Record(name_file):
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
    print("Start recording")
    stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                        input_device_index=dev_index, input=True,
                        frames_per_buffer=chunk)

    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0, int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    # getaudiodevices()
    wavefile = wave.open(wav_output_filename, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()


Record(name_file)

#samplerate, data1 = wavfile.read("input/voice-commands/test/.wav")
samplerate, data1 = wavfile.read(name_file)
times = np.arange(len(data1))/float(samplerate)

# Nếu có 2 kênh trong đoạn âm thanh thì chuyển 2 kênh về thành 1 kênh
data = []
if len(data1.shape) == 2:
    if data1.shape[1] != 1:
        for i in range(len(data1)):
            data.append(data1[i][1])
else:
    data = data1

# Chia đoạn âm thanh thành các Frames
frames = (float)((len(data) / samplerate))
frames = (int)(frames*100)

# Draw audio file
fig, ax = plt.subplots(2)


def Calculate_Energy(data, frames):
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


def DetectVoice(E, data):
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
    print(draw)

    if (len(draw) >= 2):  # nếu phát hiện được số lượng vị trí khung có tiếng nói thì thực thi
        print("VOICE DETECT")

        ax[0].set_title("Tín hiệu ")
        ax[0].set_xlabel('time')
        ax[0].set_ylabel('amplitude')
        ax[0].plot(times, data)
        ax[1].set_xlabel('index of frames')
        ax[1].set_ylabel('amplitude')
        ax[1].plot(E[0:int(frames)])
        ax[1].set_title('Năng lượng E')
        ax[1].axhline(y=nguong_y, color='r', linestyle='--')
        for i in draw:
            ax[1].axvline(i, ymin=0, ymax=1, linewidth=2,
                          linestyle="-.", color='orange')
        plt.show()
    else:
        print("NO VOICE DETECT")


E = Calculate_Energy(data, frames)
DetectVoice(E, data)
