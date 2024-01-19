import pyaudio
import numpy as np
import madmom
import time
import midi_tools as mt
import sys
from Metronome import Metronome
import MetronomeAudio
import threading

'''
This script records audio using pyaudio then analyses it using the MetronomeAudio module
It then prints a beat counter which prints beats in time to the playing audio

It is intended to work on music with a fixed bpm 
such as electronic dance music or pop music
'''




def print_audio_device_list(audio: pyaudio):
    for i in range(audio.get_device_count()):
        print(audio.get_device_info_by_index(i))



out_ports = mt.user_midi_output(1)
out_port = out_ports['MiniFuse 4 MIDI Out 1']

default_chunksize   = 8192
default_format      = pyaudio.paInt16
default_channels    = 1
default_samplerate  = 44100
record_seconds      = 4

out_port.send(mt.stop)

# data_full = np.array(data_full)
# time_process = time.time()


current_metronome = None

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class AudioProcessThread():
    def __init__(self):
        self.start_time = 0
        self.data_full = []
        self.current_metronome = None
        self.stop_process = False
        self.audio = pyaudio.PyAudio()
    
    def stop(self):
        self.stop_process = True

    @threaded
    def run(self):
        print("start run")
        while not self.stop_process:
            self.record()
            
            # process the audio to generate features
            beats, when_beats, beat_step, first_downbeat = MetronomeAudio.process_audio(self.start_time, np.array(self.data_full))
            if self.current_metronome == None:
                self.current_metronome = Metronome(first_downbeat - 0.04, beat_step, out_port) 
            else:
                self.current_metronome.update_metronome(first_downbeat - 0.04, beat_step)
            # first_downbeat-0.04 seems to keep it synced better 
            # TODO - figure out how to calibrate this
            
        print("stop run")

    def record(self): 
        print("recording")
        self.data_full = []
        stream = self.audio.open(
            input_device_index = 1, # use this to select other input devices
            format=default_format,
            channels=default_channels,
            rate=default_samplerate,
            input=True,
            frames_per_buffer=default_chunksize,
        )
        data = stream.read(default_chunksize)
        first_time = time.time()
        nums = np.fromstring(data, np.int16)
        self.data_full.extend(nums)
        for i in range(1, int(default_samplerate / default_chunksize * record_seconds)):
            data = stream.read(default_chunksize)
            nums = np.fromstring(data, np.int16)
            self.data_full.extend(nums)

        stream.stop_stream()
        stream.close()

        # this is how we estimate the start time of the audio stream
        self.start_time = first_time  - float(default_chunksize) / default_samplerate

        print("finished recording")
        

# find key
# key = madmom.features.key.CNNKeyRecognitionProcessor()(data_full)
# is_key = np.argmax(key)
# maj_min = is_key / 12
# note = 57 + is_key % 12
# print(note)


audio_process_thread = AudioProcessThread()
audio_process_thread.run()

while audio_process_thread.current_metronome == None:
    time.sleep(1)

try:
    while 1:
        audio_process_thread.current_metronome.play()
        time.sleep(0.000001)
except KeyboardInterrupt:
    print("KBD INTERUPT")
finally:
    audio_process_thread.stop()
    out_port.send(mt.stop)
    exit(1)
