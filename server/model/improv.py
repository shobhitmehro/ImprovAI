import tensorflow.keras as keras
import json
import numpy as np
from tensorflow.keras.optimizers.legacy import Adam
import music21 as m21

MAP_PATH = "/Users/shobhitmehrotra/Desktop/Projects/improvai/backend/model/data/mapping.json"

SEQUENCE_LEN = 64


class improvGenerator():
    def __init__(self, model_path="/Users/shobhitmehrotra/Desktop/Projects/improvai/server/model/model.keras"):
        self.model_path = model_path
        self.model = keras.models.load_model(model_path, compile=False)  

        self.model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy')

        with open(MAP_PATH, "r") as fp:
            self._mappings = json.load(fp)
        self._start_symbols = ["/"] * SEQUENCE_LEN
    
    def generate_improv(self, seed, num_steps, max_sequence_length, temperature):
        seed = seed.split()

        improv = seed
        seed = self._start_symbols + seed

        seed = [self._mappings.get(syb) for syb in seed]
        print(seed)

        for _ in range(num_steps):
            #stops at max seq length
            seed = seed[-max_sequence_length:]

            encode_seed = keras.utils.to_categorical(seed, num_classes=len(self._mappings))
            encode_seed = encode_seed[np.newaxis,...]

            distribution = self.model.predict(encode_seed)[0]

            output_int = self._sample_with_temperature(distribution, temperature)

            seed.append(output_int)

            #map back
            output_syb = [k for k, v in self._mappings.items() if v == output_int]
            output_syb = output_syb[0]
            if output_syb == '/':
                break
            improv.append(output_syb)

        return improv

    def _sample_with_temperature(self, distribution, temperature):

        pred = np.log(distribution)/temperature
        distribution = np.exp(pred) / np.sum(np.exp(pred))

        choices = range(len(distribution))
        ind = np.random.choice(choices, p=distribution)

        return ind
    
    def save_improv(self, improv, step_duration=0.25, format='midi', file_name="file.midi"):

        stream = m21.stream.Stream()

        start_syb = None
        step_count = 1

        for i, syb in enumerate(improv):
            if syb != "_" or i+1 == len(improv ):
                if start_syb is not None:
                    q_length = step_duration*step_count 

                    if start_syb == "r":
                        m21_event = m21.note.Rest(quarterLength=q_length)
                    else:
                        m21_event = m21.note.Note(int(start_syb), quarterLength = q_length)
                    stream.append(m21_event)

                    step_count=1

                start_syb=syb


            else: step_count+=1
        stream.write(format, file_name)

        return stream

ig = improvGenerator()
seed = "72 _ _ _ 67 _ 64 _ 71" 

line = ig.generate_improv(seed, 500, SEQUENCE_LEN, 0.7)
stm = ig.save_improv(line)
print(line)
stm.show()