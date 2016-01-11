__author__ = 'hsercanatli'

from numpy import median, mean, std
from numpy import delete
from numpy import histogram

class PitchPostFilter:
    def __init__(self):
        pass

    def energy_filter(self, threshold=0.002):
        """
        checks the saliences
        """
        for element in self.pitch:
            if element[2] <= threshold and element[1] != 0:
                element[1] = 0
                element[2] = 0

    def decompose_into_chunks(self, bottom_limit=0.7, upper_limit=1.3):
        """
        decomposes the given pitch track into the chunks.
        """
        pitch_chunks = []
        temp_pitch = [self.pitch[0]]

        # starts at the first sample
        for i in range(1, len(self.pitch) - 1):
            # separation of the zero chunks
            if self.pitch[i][1] == 0:
                if self.pitch[i + 1][1] == 0:
                    temp_pitch.append(self.pitch[i + 1])

                else:
                    temp_pitch.append(self.pitch[i])
                    if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)
                    temp_pitch = []
            # non-zero chunks
            else:
                interval = float(self.pitch[i + 1][1]) / float(self.pitch[i][1])
                if bottom_limit < interval < upper_limit:
                    temp_pitch.append(self.pitch[i])
                else:
                    temp_pitch.append(self.pitch[i])
                    if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)
                    temp_pitch = []
        if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)
        self.pitch_chunks = pitch_chunks

    def post_filter_chunks(self, chunk_limit=50):
        """
        Postfilter for the pitchChunks
        deletes the zero chunks
        deletes the chunks smaller than 50 samples(default)
        """
        self.decompose_into_chunks(0.7, 1.3)

        # deleting small Chunks
        small_chunks = [ii for ii in range(0, len(self.pitch_chunks)) if len(self.pitch_chunks[ii]) <= chunk_limit]

        # for i in small_chunks: print(len(pitch_chunks[i]), pitch_chunks[i])
        # replacing the small chunks with 0 hz
        for ind in small_chunks:
            for element in self.pitch_chunks[ind]:
                element[1] = 0
                element[2] = 0

        self.recompose_chunks()

    def recompose_chunks(self):
        """
        recomposes the given pitch chunks as a new pitch track
        """
        self.pitch = [self.pitch_chunks[i][j] for i in range(len(self.pitch_chunks))
                      for j in range(len(self.pitch_chunks[i]))]

    @staticmethod
    def are_close(num1, num2):
        d = abs(num1 - num2)
        av = (num1 + num2) / 2

        if av == 0:
            return True
        elif (d / av) < 0.2:
            return True
        else:
            return False

    def correct_octave_errors_by_chunks(self):
        self.decompose_into_chunks(bottom_limit=0.7, upper_limit=1.3)

        zero_chunks = []
        zero_ind = []
        for j in range(len(self.pitch_chunks)):
            if float(self.pitch_chunks[j][0][1]) == 0.:
                zero_chunks.append([j, self.pitch_chunks[j]])
                zero_ind.append(j)
        self.pitch_chunks = list(delete(self.pitch_chunks, zero_ind))

        self.count_octave_correction = 0
        for i in range(1, len(self.pitch_chunks) - 1):
            if len(self.pitch_chunks[i]) <= len(self.pitch_chunks[i - 1]) * 1.2 or \
                            len(self.pitch_chunks[i]) <= len(self.pitch_chunks[i + 1]) * 1.2:

                med_chunk_i = median([element[1] for element in self.pitch_chunks[i]])
                med_chunk_follow = median([element[1] for element in self.pitch_chunks[i + 1]])
                med_chunk_prev = median([element[1] for element in self.pitch_chunks[i - 1]])

                if (self.are_close(self.pitch_chunks[i][0][1] / 2., self.pitch_chunks[i - 1][-1][1]) and
                                self.pitch_chunks[i][-1][1] / 1.5 > self.pitch_chunks[i + 1][0][1]) or \
                        (self.are_close(med_chunk_i / 2., med_chunk_prev) and
                                     med_chunk_i / 1.5 > med_chunk_follow):
                    self.count_octave_correction += 1
                    for j in range(0, len(self.pitch_chunks[i])): self.pitch_chunks[i][j][1] /= 2.

                elif (self.are_close(self.pitch_chunks[i][-1][1] / 2., self.pitch_chunks[i + 1][0][1]) and
                                     self.pitch_chunks[i][0][1] / 1.5 > self.pitch_chunks[i - 1][-1][1]) or \
                        (self.are_close(med_chunk_i / 2., med_chunk_follow) and
                                        med_chunk_i / 1.5 > med_chunk_prev):
                    self.count_octave_correction += 1
                    for j in range(0, len(self.pitch_chunks[i])): self.pitch_chunks[i][j][1] /= 2.

                # other condition
                elif self.are_close(self.pitch_chunks[i][0][1] * 2., self.pitch_chunks[i - 1][-1][1]) and \
                                        self.pitch_chunks[i][-1][1] * 1.5 < self.pitch_chunks[i + 1][0][1] or \
                        (self.are_close(med_chunk_i * 2., med_chunk_prev) and
                                        med_chunk_prev * 1.5 < med_chunk_follow):

                    self.count_octave_correction += 1
                    for j in range(0, len(self.pitch_chunks[i])): self.pitch_chunks[i][j][1] *= 2.

                elif (self.pitch_chunks[i][0][1] * 1.5 < self.pitch_chunks[i - 1][-1][1] and \
                         self.are_close(self.pitch_chunks[i][-1][1] * 2., self.pitch_chunks[i + 1][0][1])) or \
                        (self.are_close(med_chunk_prev * 2, med_chunk_follow) and med_chunk_i * 1.5 < med_chunk_prev):
                    self.count_octave_correction += 1
                    for j in range(0, len(self.pitch_chunks[i])): self.pitch_chunks[i][j][1] *= 2.

        for k in range(len(zero_chunks)): self.pitch_chunks.insert(zero_chunks[k][0], zero_chunks[k][1])
        self.recompose_chunks()

    def correct_jumps(self):
        for i in range(4, len(self.pitch) - 6):
            if self.are_close(self.pitch[i - 4][1], self.pitch[i - 3][1]) and \
                    self.are_close(self.pitch[i - 3][1], self.pitch[i - 2][1]) and \
                    self.are_close(self.pitch[i - 2][1], self.pitch[i - 1][1]):

                # quadruple point
                if self.are_close(self.pitch[i + 4][1], self.pitch[i + 5][1]) and \
                        self.are_close(self.pitch[i + 5][1], self.pitch[i + 6][1]):
                    if not self.are_close(self.pitch[i][1], self.pitch[i - 1][1]) and \
                            not self.are_close(self.pitch[i][1], self.pitch[i + 4][1]):
                        self.pitch[i][1] = self.pitch[i - 1][1]
                    if not self.are_close(self.pitch[i + 3][1], self.pitch[i - 1][1]) and \
                            not self.are_close(self.pitch[i + 3][1], self.pitch[i + 4][1]):
                        self.pitch[i + 3][1] = self.pitch[i + 4][1]

                # triple point
                if self.are_close(self.pitch[i + 3][1], self.pitch[i + 4][1]) \
                        and self.are_close(self.pitch[i + 4][1], self.pitch[i + 5][1]):
                    if not self.are_close(self.pitch[i][1], self.pitch[i - 1][1]) \
                            and not self.are_close(self.pitch[i][1], self.pitch[i + 3][1]):
                        self.pitch[i][1] = self.pitch[i - 1][1]
                    if not self.are_close(self.pitch[i + 2][1], self.pitch[i - 1][1]) and \
                            not self.are_close(self.pitch[i + 2][1], self.pitch[i + 3][1]):
                        self.pitch[i + 2][1] = self.pitch[i + 3][1]

                # double point
                if self.are_close(self.pitch[i + 2][1], self.pitch[i + 3][1]) and \
                        self.are_close(self.pitch[i + 3][1], self.pitch[i + 4][1]):
                    if not self.are_close(self.pitch[i][1], self.pitch[i - 1][1]) and \
                            not self.are_close(self.pitch[i][1], self.pitch[i + 2][1]):
                        self.pitch[i][1] = self.pitch[i - 1][1]

                    if not self.are_close(self.pitch[i + 1][1], self.pitch[i - 1][1]) and \
                            not self.are_close(self.pitch[i + 1][1], self.pitch[i + 2][1]):
                        self.pitch[i + 1][1] = self.pitch[i + 2][1]

                # single point
                if self.are_close(self.pitch[i + 1][1], self.pitch[i + 2][1]) and \
                        self.are_close(self.pitch[i + 2][1], self.pitch[i + 3][1]):
                    if not self.are_close(self.pitch[i][1], self.pitch[i - 1][1]) and \
                            not self.are_close(self.pitch[i][1], self.pitch[i + 1][1]):
                        self.pitch[i][1] = self.pitch[i - 1][1]

    def correct_oct_error(self):
        pitch = [self.pitch[i][1] for i in range(len(self.pitch))]
        midf0 = (median(pitch) + mean(pitch)) / 2

        for i in range(4, len(self.pitch) - 2):
            # if previous values are continuous
            if self.are_close(self.pitch[i - 1][1], self.pitch[i - 2][1]) and \
                    self.are_close(self.pitch[i - 2][1], self.pitch[i - 3][1]) and \
                    self.are_close(self.pitch[i - 3][1], self.pitch[i - 4][1]):
                if self.pitch[i][1] > (midf0 * 1.8):
                    if self.are_close(self.pitch[i - 1][1], self.pitch[i][1] / 2.):
                        self.pitch[i][1] /= 2.
                    elif self.are_close(self.pitch[i - 1][1], self.pitch[i][1] / 4.):
                        self.pitch[i][1] /= 4.
                elif self.pitch[i][1] < (midf0 / 1.8):
                    if self.are_close(self.pitch[i - 1][1], self.pitch[i][1] * 2):
                        self.pitch[i][1] *= 2.
                    elif self.are_close(self.pitch[i - 1][1], self.pitch[i][1] * 4):
                        self.pitch[i][1] *= 4.

    def remove_extreme_values(self):
        pitch = [element[1] for element in self.pitch]
        pitch_max = max(pitch)
        pitch_mean = mean(pitch)
        pitch_std = std(pitch)

        n = list(histogram(pitch, 100))

        for i in range(0, len(n[1]) - 1):
            if n[0][i] == 0 and n[0][i + 1] == 0:
                if sum(n[0][0: i + 1]) > 0.9 * sum(n[0]):
                    pitch_max = (n[1][i] + n[1][i + 1]) / 2.

        pitch_max_cand = max(pitch_mean * 4., pitch_mean + (2 * pitch_std))
        pitch_max = min(pitch_max, pitch_max_cand)

        # max values filter
        for j in range(0, len(self.pitch)):
            if self.pitch[j][1] >= pitch_max:
                self.pitch[j][1] = 0
                self.pitch[j][2] = 0

        # min values filter
        pitch_min = pitch_mean / 4.
        for j in range(0, len(self.pitch)):
            if self.pitch[j][1] <= pitch_min:
                self.pitch[j][1] = 0
                self.pitch[j][2] = 0

    def filter_noise_region(self):
        for i in range(0, 3):

            for j in range(1, len(self.pitch) - 2):
                if not self.are_close(self.pitch[i - 1][1], self.pitch[i][1]) and \
                        self.are_close(self.pitch[i][1], self.pitch[i + 1][1]):
                    self.pitch[i][1] = 0
                    self.pitch[i][2] = 0

            for j in range(2, len(self.pitch) - 3):
                if not self.are_close(self.pitch[j - 2][1], self.pitch[j][1]) and \
                        not self.are_close(self.pitch[j - 1][1], self.pitch[j][1]) and \
                        not self.are_close(self.pitch[j + 1][1], self.pitch[j + 2][1]) and \
                        not self.are_close(self.pitch[j + 1][1], self.pitch[j + 3][1]):
                    self.pitch[j][1] = 0
                    self.pitch[j + 1][1] = 0

        for i in range(1, len(self.pitch) - 2):
            if not self.are_close(self.pitch[i - 1][1], self.pitch[i][1]) and \
                    not self.are_close(self.pitch[i][1], self.pitch[i + 1][1]) and \
                    not self.are_close(self.pitch[i + 1][1], self.pitch[i + 2][1]) and \
                    not self.are_close(self.pitch[i - 1][1], self.pitch[i + 1][1]) and \
                    not self.are_close(self.pitch[i][1], self.pitch[i + 2][1]) and \
                    not self.are_close(self.pitch[i - 1], self.pitch[i + 2][1]):
                self.pitch[i][1] = 0
                self.pitch[i][2] = 0
                self.pitch[i + 1][1] = 0
                self.pitch[i + 2][2] = 0

    def filter_chunks_by_energy(self, chunk_limit):
        self.decompose_into_chunks(bottom_limit=0.8, upper_limit=1.2)
        chunk_length = [len(element) for element in self.pitch_chunks]
        longest_chunk = self.pitch_chunks[chunk_length.index(max(chunk_length))]
        energy = [element[2] for element in longest_chunk]
        min_energy = (sum(energy) / len(energy)) / 6.
        for i in range(0, len(self.pitch_chunks)):
            temp_energy = [element[2] for element in self.pitch_chunks[i]]
            ave_energy = sum(temp_energy) / len(temp_energy)

            if ave_energy is not 0:
                if len(self.pitch_chunks[i]) <= chunk_limit or ave_energy <= min_energy:
                    for element in self.pitch_chunks[i]:
                        element[1] = 0
                        element[2] = 0
        self.recompose_chunks()

    def run(self, pitch):
        self.pitch = pitch
        self.pitch_chunks = {}

        self.count_octave_correction = 1

        for element in self.pitch:
            if element[1] == 0 or element[1] == 0.: element[1] = 0.

        self.correct_octave_errors_by_chunks()
        self.remove_extreme_values()

        self.correct_jumps()
        self.pitch = list(reversed(self.pitch))
        self.correct_jumps()
        self.pitch = list(reversed(self.pitch))

        self.filter_noise_region()

        self.correct_oct_error()
        self.pitch = list(reversed(self.pitch))
        self.correct_oct_error()
        self.pitch = list(reversed(self.pitch))

        self.correct_octave_errors_by_chunks()
        self.filter_chunks_by_energy(chunk_limit=60)

        return self.pitch
