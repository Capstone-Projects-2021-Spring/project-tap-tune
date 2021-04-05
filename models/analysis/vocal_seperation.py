import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf

filepath = '../../sampleMusic/jingleBell.wav'
songName = filepath[18:-4]
y, sr = librosa.load(filepath)
S_full, phase = librosa.magphase(librosa.stft(y))


S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))

print(S_filter)