import os
from dotenv import load_dotenv
from openai import OpenAI
import wave
import sounddevice as sd
import numpy as np
from scipy.signal import butter, lfilter

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

cur_dir = os.path.dirname(__file__)
save_directory = os.path.join(cur_dir, "..", "audio")

if not os.path.exists(save_directory):
    os.makedirs(save_directory)


class AudioResponse:
    def __init__(self, text):
        self.text = text
        # self.path = path

    def bandstop_filter(self, signal, fs, lowcut, highcut, order=2):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='bandstop')
        return lfilter(b, a, signal)

    def process(self, buffer, fs):
        signal = np.frombuffer(buffer, dtype='int16')
        # Frequencies for bandstop filters (in Hz) with narrow gaps
        bandstop_frequencies = [500, 1000, 2000, 3000, 4000]
        q_factor = 2  # Adjust this for more or less filtering effect

        # Apply each bandstop filter
        for freq in bandstop_frequencies:
            lowcut = freq - (freq / q_factor)
            highcut = freq + (freq / q_factor)
            signal = self.bandstop_filter(signal, fs, lowcut, highcut)

        return signal.astype('int16')

    def get_audio(self):
        # play audio file
        with client.with_streaming_response.audio.speech.create(
                model="tts-1-hd",
                voice="onyx",
                input=f"{self.text}",
                response_format="mp3"
        ) as response:
            audio_path = f"{save_directory}/output1.mp3"
            response.stream_to_file(audio_path)

        os.system(f"ffplay -autoexit -hide_banner -loglevel fatal {audio_path}")

        return
        # play audio file: read with wave, play with sounddevice

        with wave.open(audio_path, 'rb') as audio_file:
            print("Audio file opened")
            fs = audio_file.getframerate()
            # read all frames
            buffer = audio_file.readframes(4 * fs)
            signal = self.process(buffer, fs)
            while buffer:
                # convert binary data to integers
                # play audio
                print("Playing audio")
                sd.play(signal, fs)
                # wait until audio is done playing
                buffer = audio_file.readframes(4 * fs)
                signal = self.process(buffer, fs)
                sd.wait()
