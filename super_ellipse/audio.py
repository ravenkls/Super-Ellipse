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
        self.max_sample = self.samples.max()
        self.resolution = 100
        self.visual_delta_threshold = 1000
        self.sensitivity = 5
        self.offset = None

    def calculate_amps(self, t):
        """Calculates the amplitudes used for visualising the media."""
        if not self.offset:
            self.offset = t / 1000
        
        sample_count = int(self.song.frame_rate * 0.05)
        start_index = int(((t/1000) - self.offset) * self.song.frame_rate)
        v_sample = self.samples[start_index:start_index+sample_count]  # samples to analyse

        # use FFTs to analyse frequency and amplitudes
        fourier = np.fft.fft(v_sample)
        freq = np.fft.fftfreq(fourier.size, d=0.05)
        amps = 2/v_sample.size * np.abs(fourier)
        data = np.array([freq, amps]).T

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