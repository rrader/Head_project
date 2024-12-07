import os
import threading
import time
from random import randint, choice

from audio_recorder import VoiceRecorder
from ai_whisper import Transcription
from chatgpt_response import Response
from eyes import BenderEyes
from text_to_speech import AudioResponse

from camera import BenderCamera


def audio_loop():
    samples = VoiceRecorder()

    history = []

    while True:
        samples.record_voice()
        # if file doesn't exist, skip
        if os.path.exists("../audio/output.wav"):
            transcript = Transcription("../audio/output.wav")
            transcribed = transcript.write_speech()
            print(transcribed)
            response = Response(transcribed, history)
            r = response.get_response()
            print(r)
            audio = AudioResponse(r)
            audio.get_audio()

            history.append(
                {
                    "role": "user",
                    "content": transcribed
                }
            )
            history.append({
                "role": "assistant",
                "content": r
            })

            if len(history) > 10:
                del history[0]
        else:
            print("No audio input")


def camera_loop():
    camera = BenderCamera()

    while True:
        camera.take_picture()
        time.sleep(5)


def eyes_loop():
    eyes = BenderEyes()
    positions = [5, 7.5, 10]
    while True:
        p = choice(positions)
        print(p)
        eyes.move(p)
        time.sleep(0.5)
        eyes.move(0)
        time.sleep(randint(1, 4))


def main():
    # new thread for audio loop
    audio_thread = threading.Thread(target=audio_loop)
    audio_thread.start()

    # new thread for camera loop
    camera_thread = threading.Thread(target=camera_loop)
    camera_thread.start()

    # eyes thread
    eyes_thread = threading.Thread(target=eyes_loop)
    eyes_thread.start()

    # wait for both threads to finish
    audio_thread.join()
    camera_thread.join()


if __name__ == "__main__":
    main()
