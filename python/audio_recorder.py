import sounddevice as sd
from scipy.io.wavfile import write
import os
import numpy as np

cur_dir = os.path.dirname(__file__)
save_directory = os.path.join(cur_dir, "..", "audio")

if not os.path.exists(save_directory):
    os.makedirs(save_directory)

filename = "output.wav"
file_path = os.path.join(save_directory, filename)


class VoiceRecorder:
    def __init__(self):
        self.fs = 11025
        self.recordtime = 15
        self.recordtime = 5
        self.recordtime1 = 1
        self.channels = 1

    def record_voice(self):
        print('start recording')
        res = None
        for i in range(self.recordtime):
            myrecording = sd.rec(int(self.recordtime1 * self.fs), samplerate=self.fs, channels=self.channels)
            sd.wait()

            if res is not None:
                print(len(res))
                average_amplitude = np.mean(np.abs(res))
                average_amplitude1 = np.mean(np.abs(myrecording))
                print("Середнє значення амплітуди:", average_amplitude, average_amplitude1)
                if average_amplitude1 < average_amplitude / 3:
                    break

            if res is None:
                res = myrecording
            else:
                res = np.concatenate((res, myrecording), axis=None)
        print('ended recording')

        write(file_path, self.fs, res)
