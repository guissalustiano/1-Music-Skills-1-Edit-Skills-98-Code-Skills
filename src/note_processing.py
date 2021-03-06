from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import stft
from os import remove
from random import random

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()
def note_name(n): return NOTE_NAMES[n % 12] + str(n//12 - 1)


def splitter(array, condition):
    index = 0
    while index < len(condition):
        # optimization with np.where
        if not condition[index]:
            index += 1
            continue
        start_index = index
        while condition[index]:
            index += 1
        end_index = index

        if end_index - start_index < 40:
            continue

        yield array[start_index:end_index]


def get_limits(array):
    for a in array:
        if len(a) < 2: continue
        yield (a[0], a[-1])


def extract_subclips(video):
    filter_value = 200
    temp_filename = 'temp'

    audio = video.audio
    print("[o] Abrindo audio")
    audio.write_audiofile(f'{temp_filename}.wav')
    fps, soundarray_stereo = wavfile.read(f'{temp_filename}.wav')
    remove(f'{temp_filename}.wav')
    soundarray_mono = soundarray_stereo.sum(axis=1) / 2
    # time = np.linspace(0, len(soundarray_mono) / fps, num=len(soundarray_mono))

    print("[o] Aplicando o fft")
    sample, time_seg, zxx = stft(soundarray_mono, fs=fps)
    zxx = np.abs(zxx)
    sound_amplitude = np.dstack((zxx.sum(axis=0), time_seg))[0]

    print("[o] Descobrindo as notas")
    sound_splited = splitter(
        sound_amplitude, sound_amplitude[:, 0] > filter_value)
    limits = get_limits([elm[:, 1] for elm in sound_splited])

#    plt.plot(sound_amplitude[:, 1], sound_amplitude[:, 0])
#    for start, end in limits:
#        color = (random(), random(), random())
#        plt.axvline(x=start, color=color)
#        plt.axvline(x=end, color=color)
#    plt.show()

    for t_start, t_end in limits:
        yield video.subclip(t_start, t_end)


def extract_notes(video):
    sub_videos = list(extract_subclips(video))[1:]
    dic = {}
    print("[o] Cortando e numerando as notas")
    for index, sub_video in enumerate(sub_videos):
        note_number = 40 + index
        txtClip = TextClip(note_name(note_number), color='white', font="Verdana", kerning=5, fontsize=100)
        dic[note_number] = CompositeVideoClip([
            sub_video,
            txtClip.set_duration(sub_video.duration).set_position((10, 10))
        ])
    return dic


if __name__ == "__main__":
    video=VideoFileClip("../video.mp4")
    sub_videos=extract_notes(video)
    final_clip = concatenate_videoclips(list(sub_videos.values()))
    final_clip.write_videofile('note_processing_test.mp4')
