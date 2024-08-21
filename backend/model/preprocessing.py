import sqlite3 as sq
import pandas as pd
import numpy as np
import music21 as m21
import os
from music21 import environment

PATH = "/Users/shobhitmehrotra/Desktop/Projects/improvai/backend/model/Midi"
APP_PATH = "/Applications/MuseScore 3.app/Contents/MacOS/mscore"
from music21 import duration

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
        print(element.duration)
        
        if element.duration not in durations: 
            # Replace note with rest if the duration is not acceptable
            plug_rest = m21.note.Rest(duration=element.duration)
            new_elements.append(plug_rest)
            print("REST HERE")
        else:
            new_elements.append(element)
    
    # Clear the stream and add the new elements
    tune.flat.notesAndRests.clear()
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
            tune = m21.converter.parse(os.path.join(path, file))
            names.append(file)
            midiFiles.append(tune)
        print("MIDI Files Loaded...")
    return midiFiles, names


def preprocess():
    set_musescore_path(APP_PATH)
    files, names = load_data(PATH)
    data = filter_data(files)
    print(names[1])
    data[1].show()


if __name__ == "__main__":
    preprocess()
