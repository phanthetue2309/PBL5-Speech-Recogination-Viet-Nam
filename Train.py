import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import librosa
import numpy as np
import warnings

warnings.filterwarnings("ignore")
train_audio_path = 'input/train/'

labels=os.listdir(train_audio_path)
remove_text = '.ipynb_checkpoints'
if remove_text in labels : 
  labels.remove('.ipynb_checkpoints')
size_test = len(labels)

shape = 20800
all_wave = []
all_label = []

for label in labels:
    waves = [f for f in os.listdir(train_audio_path + '/'+ label) if f.endswith('.wav')] # get waves files
    for wav in waves:
        samples, sample_rate = librosa.load(train_audio_path + '/' + label + '/' + wav, sr = 44100) # tần số gốc
        data  = []
        if len(samples.shape) == 2:
          if samples.shape[1] !=  1 :
            for i in range(len(samples)):
              data.append(samples[i][1])
        else : 
          data = samples

        samples = librosa.resample(data, sample_rate, 16000) # resample lại còn 16000 Hz
        samples = samples[0:shape] # độ dài file lấy là 1.3s
        all_wave.append(samples)
        all_label.append(label)

from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
from sklearn.model_selection import train_test_split

le = LabelEncoder()
y=le.fit_transform(all_label)
classes= list(le.classes_)

input_shape = (shape,1)
y=np_utils.to_categorical(y, num_classes=len(labels))

all_wave = np.array(all_wave).reshape(-1,shape,1)

# use size_test in text_size has made before
x_tr, x_val, y_tr, y_val = train_test_split(np.array(all_wave),np.array(y),stratify=y,test_size = 0.2, random_state=1,shuffle=True)


from keras.layers import Dense, Dropout, Flatten, Conv1D, Input, MaxPooling1D
from keras.models import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import backend as K
K.clear_session()

inputs = Input(shape=input_shape)


#First Conv1D layer
conv = Conv1D(8,13, padding='valid', activation='relu', strides=1)(inputs)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Second Conv1D layer
conv = Conv1D(16, 11, padding='valid', activation='relu', strides=1)(conv)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Third Conv1D layer
conv = Conv1D(32, 9, padding='valid', activation='relu', strides=1)(conv)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Fourth Conv1D layer
conv = Conv1D(64, 7, padding='valid', activation='relu', strides=1)(conv)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Flatten layer
conv = Flatten()(conv)

#Dense Layer 1
conv = Dense(256, activation='relu')(conv)
conv = Dropout(0.3)(conv)

#Dense Layer 2
conv = Dense(128, activation='relu')(conv)
conv = Dropout(0.3)(conv)

outputs = Dense(len(labels), activation='softmax')(conv)

model = Model(inputs, outputs)
model.summary()

model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=10, min_delta=0.0001) 
mc = ModelCheckpoint('best_model.h5', monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')

history=model.fit(x_tr, y_tr ,epochs=200, callbacks=[es,mc], batch_size=16, validation_data=(x_val,y_val))
