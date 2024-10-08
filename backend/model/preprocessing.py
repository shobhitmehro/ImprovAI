import sqlite3 as sq
import pandas as pd
import numpy as np
import music21 as m21
import os
from music21 import environment
import json
import tensorflow as tf
from tensorflow import keras

DATASET_PATH = "/Users/shobhitmehrotra/Desktop/Projects/improvai/backend/model/data/dataset"
PATH = "/Users/shobhitmehrotra/Desktop/Projects/improvai/backend/model/data/Omnibook/MusicXml"
APP_PATH = "/Applications/MuseScore 3.app/Contents/MacOS/mscore"
SEQUENCE_LEN = 64
NEW_FILE_PATH = "/Users/shobhitmehrotra/Desktop/Projects/improvai/backend/model/data/merged_data"
MAP_PATH = "/Users/shobhitmehrotra/Desktop/Projects/improvai/backend/model/data/mapping.json"

one = m21.duration.Duration(0.25)
two = m21.duration.Duration(0.5)
three = m21.duration.Duration(0.75)
four = m21.duration.Duration(1.0)
five = m21.duration.Duration(1.25)
six = m21.duration.Duration(1.5)
seven = m21.duration.Duration(1.75)
eight = m21.duration.Duration(2.0)
nine = m21.duration.Duration(2.25)
ten = m21.duration.Duration(2.5)
eleven = m21.duration.Duration(2.75)
twelve = m21.duration.Duration(3.0)
thirteen = m21.duration.Duration(3.25)
fourteen = m21.duration.Duration(3.5)
fifteen = m21.duration.Duration(3.75)
sixteen = m21.duration.Duration(4.0)
triplet_one = m21.duration.Duration(1/3)
triplet_two =m21.duration.Duration(2/3)

DURATIONS = [one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, triplet_one, triplet_two]
def set_musescore_path(path):
    m21.environment.set('musicxmlPath', path)
    m21.environment.set('musescoreDirectPNGPath', path)    


# tune: music21 Stream object
# duration: list of acceptable durations
def filter_durations(tune, durations):
    new_elements = []

    for element in tune.flat.notesAndRests:    
        if element.duration not in durations: 
            # Replace note with rest if the duration is not acceptable
            plug_rest = m21.note.Rest(duration=element.duration)
            new_elements.append(plug_rest)
        else:
            new_elements.append(element)
    
    # Clear the stream and add the new elements
    tune.flat.notesAndRests.stream().clear()
    tune.flat.notesAndRests.elements = new_elements
    
    return tune

def filter_data(Stream):
    filtered_data = []
    for tune in Stream:
        filtered_data.append(filter_durations(tune, DURATIONS))
        
    return filtered_data


def load_data(data):
    midiFiles = []
    names = []
    for path, subdirs, files in os.walk(data):
        for file in files:
            if(file.endswith('xml')):
                tune = m21.converter.parse(os.path.join(path, file))
                names.append(file)
                midiFiles.append(tune)
        print("MIDI Files Loaded...")
    
    return midiFiles, names

def transpose_tune(tune):
    key = tune.analyze("key")
    if(key.mode == "major"):
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif(key.mode == "minor"):
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
    
    transposed_tune = tune.transpose(interval)

    return transposed_tune




def transpose_data(data):
    new_data = []
    
    for tune in data:
        new_data.append(transpose_tune(tune))
    return new_data

def encode(tune, time_step=0.25):
    encoded_tune = []
    for token in tune.flat.notesAndRests:
        syb = "--"
        if isinstance(token, m21.note.Note):
            syb = token.pitch.midi
        elif isinstance(token, m21.note.Rest):
            syb = "r"
        steps = int(token.duration.quarterLength/time_step)

        for step in range(steps):
            if step == 0:
                encoded_tune.append(syb)
            else: encoded_tune.append("_")
    
    encoded_tune = " ".join(map(str,encoded_tune))

    return encoded_tune

def merge_data(old_path, new_path, length):
    delimeter = "/ "*length
    tunes = ""

    for path, _, files in os.walk(old_path):
        for file in files:
            file_path = os.path.join(path, file)
            tune = load(file_path)
            tunes = tunes + tune + " " +delimeter
    tunes = tunes[:-1]

    with open(os.path.join(new_path, "merged_dataset.txt"), "w") as fp:
        fp.write(tunes)
    return tunes


def load(path):
    with open(path, "r") as fp:
        tune = fp.read()
    return tune

def to_json(tunes,map_path):
    hm = {}
    tunes = tunes.split()

    
    vocab = list(set(tunes)) 

    for i, syb in enumerate(vocab):
        hm[syb] = i


    with open(map_path, "w") as fp:
        json.dump(hm, fp, indent=4)

def to_int(tunes):
    tunes_in_int = []

    with open(MAP_PATH, "r") as fp:
        map = json.load(fp)
    
    tunes = tunes.split()

    for syb in tunes:
        tunes_in_int.append(map.get(syb))
    
    return tunes_in_int

def generate_train_sequence(sequence_len):
    tunes = load(os.path.join(NEW_FILE_PATH, "merged_dataset.txt")) 
    int_songs = to_int(tunes)
    num_sequences = len(int_songs) - sequence_len
    inputs = []
    targets = []

    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_len])
        targets.append(int_songs[i+sequence_len])
 
    vocab_size = len(set(int_songs))
    inputs = tf.keras.utils.to_categorical(inputs, num_classes=vocab_size)
    targets = np.array(targets)

    return inputs, targets



def preprocess(data_path):
    

    files, names = load_data(data_path)
    data = filter_data(files)
    transposed_data = transpose_data(data)


    for i, tune in enumerate(transposed_data):

        encoded_tune = encode(tune)

        path = os.path.join(DATASET_PATH,str(tune.metadata.title))
        with open(path, "w") as fp:
            fp.write(encoded_tune)


     

def main():
    set_musescore_path(APP_PATH)
    preprocess(PATH)  
    merged_data = merge_data(DATASET_PATH, NEW_FILE_PATH, SEQUENCE_LEN)
    to_json(merged_data, MAP_PATH)
    inputs, targets = generate_train_sequence(SEQUENCE_LEN)

    print(f"Inputs: {inputs.shape}")
    print(f"Targets: {targets.shape}")
         
if __name__ == "__main__":
    main()