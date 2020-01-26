# std
import time
import os

# other
from pydub import AudioSegment
import numpy as np


class SongAnalysis:

    def __init__(self, song):
        super().__init__()
        self.song = AudioSegment.from_file(song).set_channels(1)
        self.samples = np.asarray(self.song.get_array_of_samples())
        self.sub_samples = np.array_split(self.samples, self.song.duration_seconds*20)
        self.fft_data = []

        for sample_set in self.sub_samples:
            fourier = np.fft.fft(sample_set)
            freq = np.fft.fftfreq(fourier.size, d=0.05)
            amps = 2/sample_set.size * np.abs(fourier)
            data = np.array([freq, amps]).T
            self.fft_data.append((freq, amps, data))

        self.max_sample = self.samples.max()
        self.resolution = 100
        self.visual_delta_threshold = 1000
        self.sensitivity = 5
        self.offset = None

    def calculate_amps(self, t):
        """Calculates the amplitudes used for visualising the media."""
        if not self.offset:
            self.offset = t
        
        index = round((t - self.offset) * 20 / 1000)
        freq, amps, data = self.fft_data[index]


        point_range = 1 / self.resolution
        point_samples = []

        if not data.size:
            return

        for n, f in enumerate(np.arange(0, 1, point_range), start=1):
            # get the amps which are in between the frequency range
            amps = data[(f - point_range < data[:, 0]) & (data[:, 0] < f)]
            if not amps.size:
                point_samples.append(0)
            else:
                point_samples.append(amps.max()*((1+self.sensitivity/10+(self.sensitivity-1)/10)**(n/50)))

        # they are divided by the highest sample in the song to normalise the
        # amps in terms of decimals from 0 -> 1
        return point_samples / self.max_sample

    @property
    def duration(self):
        return self.song.duration_seconds