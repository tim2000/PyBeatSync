# AutoClock

Fork from https://github.com/louischaman/PyBeatSync

Updated to python 3.9 (but need numpy 1.19 because madmom is not supported anymore)

I have modified metronome_basic.py to always compute the BPM in parallel and update the metronome. 

My goal is to make it works on a raspberry pi with a USB ADC, a serial Midi Board and a 7 segment display in order to add it as a stadalone in in my turntable setup.

I may add the key detection later on.
