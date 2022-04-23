import numpy as np
import sys, getopt, os
from extract_data import extract_data

def reduce_lex(words):
    # reduce lexicon
    words_unique = set(words)
    ref = dict()

    with open("lex_big.txt") as f:
        for line in f:
            line = line.strip()
            columns = line.split(" ",1)
            word = columns[0]
            pron = columns[1]
            try: 
                ref[word].append(pron)
            except:
                ref[word] = list()
                ref[word].append(pron)

    lex = open("data/local/dict/lexicon.txt",'w')
    # lex.write('!SIL SIL\n')
    # lex.write('<UNK> SPN\n')
    # lex.write('<OOV> <oov>\n')
    for word in words_unique:
        if word in ref.keys():
            for pron in ref[word]:
                lex.write(f'{word.lower()} {pron.lower()}\n')
        else:
            print(f'Word not in lexicon: {word}')

def prep_dir(dir):
    fold = dir.split(sep='/')[-1]
    file_names = os.listdir(f'emg/{fold}')
    file_names.sort()

    text = open(os.path.join(dir,'text'),'w')
    wavscp = open(os.path.join(dir,'wav.scp'),'w')
    u2s = open(os.path.join(dir,'utt2spk'),'w')

    for fname in file_names:
        if(fname[0] != '.'):
            tokens = fname.split(sep='.')[0].split(sep='_')
            sess = tokens[0]
            word = tokens[1]
            ind = tokens[2]

            # write to text
            utt_id = f'{sess}_{word}_{ind}'
            text.write(f'{utt_id}\t{word}\n')

            # write to wav.scp
            emg = '/home/adithyashok/Dev/Bitalino/kaldi/egs/silent-speech-kaldi/emg/'
            path = os.path.join(emg, fold)
            fname = utt_id + '.wav'
            fullpath = path + '/' + fname
            wavscp.write(f'{utt_id}\t{fullpath}\n')

            # write to utt2spk
            u2s.write(f'{utt_id}\t{sess}\n')


def main(argv):
    train_dir = ""; test_dir = ""; lex = False; fname = ""
    try:
        opts, args = getopt.getopt(argv,"t:v:lf", \
            ['train-dir=','test-dir=','lexicon=','filename='])
    except getopt.GetoptError:
        print('data_prep.py -t <train-dir> -v <test-dir> -l <lexicon>')
        sys.exit(2)

    # print(opts)

    for opt, arg in opts:
        if opt in ('-l','--lexicon'):
            lex = arg.lower() == 'true'
        elif opt in ('-t','--train-dir'):
            train_dir = arg
        elif opt in ('-v','--test-dir'):
            test_dir = arg
        elif opt in ('-f','--filename'):
            fname = arg
    
    if lex:
        signal = os.path.join("./raw/",f'{fname}.txt')
        times = os.path.join("./raw/",f'{fname}_times.txt')
        _, words, _, _ = extract_data(signal, times)
        reduce_lex(words)

    prep_dir(train_dir)
    prep_dir(test_dir)

if __name__ == "__main__":
   main(sys.argv[1:])
