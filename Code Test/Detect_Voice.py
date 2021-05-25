from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
import math

samplerate, data1 = wavfile.read("test.wav")

times = np.arange(len(data1))/float(samplerate)
dt = 1/samplerate

data = []
if len(data1.shape) == 2:
    if data1.shape[1] != 1:
        for i in range(len(data1)):
            data.append(data1[i][1])
else:
    data = data1

frames = (float)((len(data) / samplerate))
fig, ax = plt.subplots(2)
ax[0].set_title("Tín hiệu ")
ax[0].set_xlabel('time')
ax[0].set_ylabel('amplitude')
ax[0].plot(times, data)

frames = (int)(frames*100)
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


def DetectVoice(E):
    '''
    Tìm ngưỡng năng lượng chuẩn bị
    '''
    nguong_E = 5*100000000  # 5x10^8 ngưỡng mặc định ứng với mic ghi âm
    maxE = max(E)
    if maxE < nguong_E:
        print("NO VOICE")
    else:
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

        ax[0].set_title("Tín hiệu ")
        ax[0].set_xlabel('time')
        ax[0].set_ylabel('amplitude')
        ax[0].plot(times, data)
        ax[1].set_xlabel('index of frames')
        ax[1].set_ylabel('amplitude')
        ax[1].plot(E[0:int(frames)])
        ax[1].set_title('Năng lượng E')
        ax[1].axhline(y=nguong_y, color='r', linestyle='--')


E = Calculate_Energy(data, frames)
DetectVoice(E)
plt.show()
