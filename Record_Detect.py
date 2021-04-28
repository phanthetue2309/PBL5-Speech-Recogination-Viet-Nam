import pyaudio
import wave
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np
def getaudiodevices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i).get('name'))
#getaudiodevices()
name_file = "test.wav"

def Record(name_file):
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 4 # seconds to record

    dev_index = 0 # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = name_file # name of .wav file

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    print("Start recording")
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)

    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    #getaudiodevices()
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

Record(name_file)

#samplerate, data1 = wavfile.read("input/voice-commands/test/.wav")
samplerate, data1 = wavfile.read(name_file)
times = np.arange(len(data1))/float(samplerate)

# Solution with 2 channels
data  = []
if len(data1.shape) == 2:
    if data1.shape[1] !=  1 :
        for i in range(len(data1)):
            data.append(data1[i][1])
else : 
    data = data1

frames = (float)((len(data) / samplerate))
frames = (int)(frames*100)

# Draw audio file 
fig, ax = plt.subplots(3)
ax[0].set_title("Tín hiệu ")
ax[0].set_xlabel('time')
ax[0].set_ylabel('amplitude') 
ax[0].plot(times,data)

def Calculate_Energy(data, frames):
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

def Detect_Split_Voice(E):
    nguong_E = 5*100000000 # 5x10^8
    maxE = max(E)
    if maxE < nguong_E : 
        print("NO VOICE")
    else : 
        E = E / maxE
        draw = [] 
        new_list = []
        nguong_y = 0.1
        check = 0
        for m in range(0,len(E) - 3) :
            if(E[m] > nguong_y and check==0) :
                a = True
                for i in range(m,m+3) :
                    if (E[i] < nguong_y) :
                        a = False
                        break
                if (a == True) :
                    draw.append(m)
                    check = 1
            elif (E[m] < nguong_y and check==1) :
                a=True
                for i in range(m,m+3):
                    if (E[i] > nguong_y):
                        a=False
                        break
                if(a==True):
                    draw.append(m-1)
                    check = 0
        print(draw)       

        # ax[1].set_xlabel('index of frames')
        # ax[1].set_ylabel('amplitude')         
        # ax[1].plot(E[0:int(frames)])
        # ax[1].set_title('Năng lượng E')
        # ax[1].axhline(y=nguong_y, color='r', linestyle='--')  

        if (len(draw) >= 3 ):
            print("VOICE DETECT")
            new_list = E[draw[0] : draw[-1]]
            max_length = 50

            if (len(new_list) > max_length) :
                different = len(new_list) - max_length
                first_part = E[draw[0]:draw[1]]
                second_part = E[draw[1] + different + 1: draw[-1] + 1 ]    # để có thẻe lấy thêm thằng cuối       
                new_list =  np.concatenate((first_part, second_part))

            elif len(new_list) < max_length :
                different = len(new_list) - max_length
                list_choices = E[draw[1] : draw[1] + different ]  # chọn chuỗi muốn thêm
                first_part = E[draw[0] : draw[1]]
                second_part = E[draw[1] + different + 1  : draw[-1] + 1]    # để có thẻe lấy thêm thằng cuối    
                new_list = np.concatenate((first_part,list_choices, second_part))
              
            with open("text.txt", "w") as output:
                output.write(str(new_list))   
            
            ax[2].plot(new_list)
        
        else:
            print("NO VOICE DETECT")
            
E = Calculate_Energy(data, frames)
Detect_Split_Voice(E)
plt.show()