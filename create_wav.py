import sys, getopt, os
import numpy as np
from extract_data import extract_data
import scipy.io.wavfile as wavf
import matplotlib.pyplot as plt
from scipy.signal import filtfilt, butter, iirnotch

def rescale_data(data):
    # apply filters
    b_notch, a_notch = iirnotch(60, 30, 1000)
    low_cutoff, high_cutoff = 20, 450
    b, a = butter(10, [low_cutoff, high_cutoff], fs=1000, btype='bandpass')
    data = filtfilt(b_notch, a_notch, data, axis=0) # 60 Hz notch for power line noise
    data = filtfilt(b, a, data, axis=0) # Bandpass for emg freq range

    # convert back to ADC value
    data[:,0:4] = (data[:,0:4]/1000*1009/3.3 + 0.5)*(2**10)
    data[:,4:] = (data[:,4:]/1000*1009/3.3 + 0.5)*(2**6)

    # center at 0
    data[:,0:4] = (data[:,0:4] - 512) * (2**6)
    data[:,4:] = (data[:,4:] - 32) * (2**10)

    return data.astype(dtype='int16')

def vis(data, starts, ends):
    plt.figure(figsize=(20,8))
    for i in range(6):
        plt.subplot(6,1,i+1)
        plt.plot(data[:,i]); plt.ylim(plt.ylim())
        plt.vlines(starts,-32768,32768,'g')
        plt.vlines(ends,-32768,32768,'r')

    plt.tight_layout()
    plt.show()

def create_wav(data, words, starts, ends, session, num_train, num_test):
    # rescale data
    data = rescale_data(data)
    vis(data, starts, ends)
    words = np.array(words)
    
    # train-test split
    # sort
    num_tot = num_train + num_test
    sort_inds = np.argsort(words)
    words = words[sort_inds]; 
    starts = starts[sort_inds]
    ends = ends[sort_inds]

    # split
    num_unique = len(set(words))
    train_tot = num_train * num_unique; test_tot = num_test * num_unique
    words_train = np.zeros(train_tot, dtype='object'); words_test = np.zeros(test_tot, dtype='object');  
    starts_train = np.zeros(train_tot, dtype=int); starts_test = np.zeros(test_tot, dtype=int)
    ends_train = np.zeros(train_tot, dtype=int); ends_test = np.zeros(test_tot, dtype=int)

    for i in range(len(words)):
        train_start = i * num_tot; train_end = train_start + num_train
        test_start = i * num_tot + num_train; test_end = test_start + num_test

        words_train[i*num_train:(i+1)*num_train] = words[train_start:train_end]
        starts_train[i*num_train:(i+1)*num_train] = starts[train_start:train_end]
        ends_train[i*num_train:(i+1)*num_train] = ends[train_start:train_end]

        words_test[i*num_test:(i+1)*num_test] = words[test_start:test_end]
        starts_test[i*num_test:(i+1)*num_test] = starts[test_start:test_end]
        ends_test[i*num_test:(i+1)*num_test] = ends[test_start:test_end]

    fs = 1000
    train_dir = "emg/train/"; test_dir = "emg/test/"
    for i, word in enumerate(words_train):
        # convert to and write wav
        samples = data[starts_train[i]:ends_train[i],:]
        out_f = os.path.join(train_dir,f'sess{session}_{word}_{i%num_train}.wav')
        wavf.write(out_f, fs, samples)

    for i, word in enumerate(words_test):
        # convert to and write wav
        samples = data[starts_test[i]:ends_test[i],:]
        out_f = os.path.join(test_dir,f'sess{session}_{word}_{i%num_test}.wav')
        wavf.write(out_f, fs, samples)

def main(argv):
    fname = ''; num_train = ''; num_test = ''; session = ''
    try:
        opts, args = getopt.getopt(argv,"f:t:v:s:", \
            ['file=','train=','test=','session='])
    except getopt.GetoptError:
        print('create_wav.py -f <filename> -t <num-train> -v <num-test> -s <session>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-f","--file"):
            fname = arg
        elif opt in ("-t","--train"):
            num_train = int(arg)
        elif opt in ("-v","--test"):
            num_test = int(arg)
        elif opt in ("-s","--session"):
            session = arg

    signal = os.path.join("./raw/",f'{fname}.txt')
    times = os.path.join("./raw/",f'{fname}_times.txt')
    data, words, starts, ends = extract_data(signal, times)

    create_wav(data, words, starts, ends, session, num_train, num_test)

if __name__ == "__main__":
   main(sys.argv[1:])

