import numpy as np
import json
import dateutil.parser
import matplotlib.pyplot as plt

def extract_data(signal, timestamps):
    '''
    Extracts signal data and word info from files.

    Args:
        signal (str):  absolute or relative filepath to the .txt file generated by Bitalino software.
        timestamps (str): absolute or relative filepath to the .txt file generated by the data collection script.

    Returns:
        data (numpy array): n x 6 array containing signal data in mV. First 4 columns are 10-bit channels, last 2 are 6-bit.
        words (string list): list of words in order
        starts (numpy array): start times of words relative to beginning of signal
        ends (numpy array): end times of words relative to beginning of signal   
    '''

    # get the start time
    f = open(signal)
    lines = f.readlines()
    mac = lines[1][4:21]
    header = json.loads(lines[1][2:])[mac]
    start_time = header['date'][:5] + "0" + header['date'][5:] + "T" + header['time'] + "-05"
    # print(start_time)
    start_time = int(dateutil.parser.isoparse(start_time).timestamp()*1000)

    # extract data and convert to voltage in mV
    data = np.loadtxt(signal)[:,-6:]
    data[:,0:4] = (data[:,0:4]/(2**10)-0.5)*3.3/1009*1000
    data[:,4:] = (data[:,4:]/(2**6)-0.5)*3.3/1009*1000
    
    # process timestamps
    words = []
    starts = []
    ends = []
    f = open(timestamps)
    for l in f.readlines():
        toks = l.split()
        if toks[1] == 'start:':
            words.append(toks[0])
            starts.append(int(int(toks[2])/1000000))
        else:
            ends.append(int(int(toks[2])/1000000))

    starts = np.array(starts) - start_time + 770
    ends = np.array(ends) - start_time + 770

    return data, words, starts, ends

