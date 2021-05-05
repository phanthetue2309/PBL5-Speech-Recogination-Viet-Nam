from scipy.io import wavfile
import matplotlib.pyplot as plt 
import numpy as np
import math

#samplerate, data1 = wavfile.read("input/voice-commands/test/.wav")
#samplerate, data1 = wavfile.read("input/train_split/đi tới/ditoi_tue_01.wav")
samplerate, data1 = wavfile.read("test.wav")

times = np.arange(len(data1))/float(samplerate)
dt = 1/samplerate

data  = []
if len(data1.shape) == 2:
    if data1.shape[1] !=  1 :
        for i in range(len(data1)):
            data.append(data1[i][1])
else : 
    data = data1

frames = (float)((len(data) / samplerate))
fig, ax = plt.subplots(2)
ax[0].set_title("Tín hiệu ")
ax[0].set_xlabel('time')
ax[0].set_ylabel('amplitude') 
ax[0].plot(times,data)

k = 1
frames = (int)(frames*100)
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

maxE = max(E)
minE = min(E)
E = E / maxE

#nguong_y = 5*100000000 # 5x10^8
draw = []
m = 0
nguong_y = 0.1

check = 0
while (m < len(E) - 3):
    if(E[m] > nguong_y and check==0) :
        a = True
        for i in range(m,m+3) :
            if (E[i] < nguong_y) :
                a = False
                break
        if (a == True) :
            draw.append(m)
            check=1
    elif(E[m] < nguong_y and check==1) :
        a=True
        for i in range(m,m+3):
            if (E[i] > nguong_y):
                a=False
                break
        if(a==True):
            draw.append(m-1)
            check=0
    m=m+1

print(draw)       

ax[1].set_xlabel('index of frames')
ax[1].set_ylabel('amplitude')         
ax[1].plot(E)
ax[1].set_title('Năng lượng E')
ax[1].axhline(y=nguong_y, color='r', linestyle='--')  

if (len(draw) > 2 ):
    print("VOICE DETECT")
else:
    print("NO VOICE DETECT")
plt.show()

