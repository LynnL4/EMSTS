#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import wave
import numpy

if len(sys.argv) < 2:
    print('Usage: python {} audio-file.wav'.format(sys.argv[0]))
    sys.exit(1)

wav = wave.open(sys.argv[1], 'rb')
channels = wav.getnchannels()
fs = wav.getframerate()
N  = wav.getnframes()
if N > fs:
    N = fs
frames = wav.readframes(N)
wav.close()

print("channels    : %d" % channels, file=sys.stderr)
print("rate        : %d" % fs, file=sys.stderr)
print("file frames : %d" % wav.getnframes(), file=sys.stderr)
print("FFT  frames : %d" % N, file=sys.stderr)

wave_data = numpy.fromstring(frames, dtype=numpy.short)
# To channels column, auto row count
wave_data.shape = -1,channels
wave_data = wave_data.T

def max_power_freq():
    start = 0

    df = fs / N
    freq = [df * n for n in range(0, N)]

    data_chan_0 = wave_data[0][start + 0: start + N]
    c = numpy.fft.fft(data_chan_0) * 2 / N

    d = int(len(c) / 2) - 1
    while freq[d] > 4000:
        d -= 1

    index = 0
    v = -1.0
    for i in range(1, d):
        # print("FREQ[{}] V[{}]".format(freq[i], abs(c[i])))
        if abs(c[i]) > v:
            index = i
            v = abs(c[i])

    return freq[index]

f = int(max_power_freq())
print("MAX-Power-Freq={}".format(f))

quit(0)
