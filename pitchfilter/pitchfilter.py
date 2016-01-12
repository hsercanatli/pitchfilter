__author__ = 'hsercanatli'

from numpy import median, mean, std
from numpy import delete
from numpy import histogram

class PitchPostFilter:
    def __init__(self, energy_threshold=0.002, bottom_limit=0.7, upper_limit=1.3, chunk_limit=50):
        self.energy_threshold = energy_threshold
        self.bottom_limit = bottom_limit
        self.upper_limit = upper_limit
        self.chunk_limit = chunk_limit

    def decompose_into_chunks(self, pitch, bottom_limit, upper_limit):
        """
        decomposes the given pitch track into the chunks.
        """
        pitch_chunks = []
        temp_pitch = [pitch[0]]

        # starts at the first sample
        for i in range(1, len(pitch) - 1):
            # separation of the zero chunks
            if pitch[i][1] == 0:
                if pitch[i + 1][1] == 0:
                    temp_pitch.append(pitch[i + 1])

                else:
                    temp_pitch.append(pitch[i])
                    if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)
                    temp_pitch = []
            # non-zero chunks
            else:
                interval = float(pitch[i + 1][1]) / float(pitch[i][1])
                if bottom_limit < interval < upper_limit:
                    temp_pitch.append(pitch[i])
                else:
                    temp_pitch.append(pitch[i])
                    if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)
                    temp_pitch = []
        if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)

        return pitch_chunks

    def recompose_chunks(self, pitch_chunks):
        """
        recomposes the given pitch chunks as a new pitch track
        """
        pitch = [pitch_chunks[i][j] for i in range(len(pitch_chunks))
                      for j in range(len(pitch_chunks[i]))]
        return pitch

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

    def correct_octave_errors_by_chunks(self, pitch):
        pitch_chunks = self.decompose_into_chunks(pitch=pitch, bottom_limit=self.bottom_limit,
                                                  upper_limit=self.upper_limit)

        zero_chunks = []
        zero_ind = []
        for j in range(len(pitch_chunks)):
            if float(pitch_chunks[j][0][1]) == 0.:
                zero_chunks.append([j, pitch_chunks[j]])
                zero_ind.append(j)
        pitch_chunks = list(delete(pitch_chunks, zero_ind))

        count_octave_correction = 0
        for i in range(1, len(pitch_chunks) - 1):
            if len(pitch_chunks[i]) <= len(pitch_chunks[i - 1]) * 1.2 or \
                            len(pitch_chunks[i]) <= len(pitch_chunks[i + 1]) * 1.2:

                med_chunk_i = median([element[1] for element in pitch_chunks[i]])
                med_chunk_follow = median([element[1] for element in pitch_chunks[i + 1]])
                med_chunk_prev = median([element[1] for element in pitch_chunks[i - 1]])

                if (self.are_close(pitch_chunks[i][0][1] / 2., pitch_chunks[i - 1][-1][1]) and
                                pitch_chunks[i][-1][1] / 1.5 > pitch_chunks[i + 1][0][1]) or \
                        (self.are_close(med_chunk_i / 2., med_chunk_prev) and
                                     med_chunk_i / 1.5 > med_chunk_follow):
                    for j in range(0, len(pitch_chunks[i])): pitch_chunks[i][j][1] /= 2.

                elif (self.are_close(pitch_chunks[i][-1][1] / 2., pitch_chunks[i + 1][0][1]) and
                                     pitch_chunks[i][0][1] / 1.5 > pitch_chunks[i - 1][-1][1]) or \
                        (self.are_close(med_chunk_i / 2., med_chunk_follow) and
                                        med_chunk_i / 1.5 > med_chunk_prev):
                    for j in range(0, len(pitch_chunks[i])): pitch_chunks[i][j][1] /= 2.

                # other condition
                elif self.are_close(pitch_chunks[i][0][1] * 2., pitch_chunks[i - 1][-1][1]) and \
                                        pitch_chunks[i][-1][1] * 1.5 < pitch_chunks[i + 1][0][1] or \
                        (self.are_close(med_chunk_i * 2., med_chunk_prev) and
                                        med_chunk_prev * 1.5 < med_chunk_follow):
                    for j in range(0, len(pitch_chunks[i])): pitch_chunks[i][j][1] *= 2.

                elif (pitch_chunks[i][0][1] * 1.5 < pitch_chunks[i - 1][-1][1] and
                          self.are_close(pitch_chunks[i][-1][1] * 2., pitch_chunks[i + 1][0][1])) or \
                        (self.are_close(med_chunk_prev * 2, med_chunk_follow) and med_chunk_i * 1.5 < med_chunk_prev):
                    for j in range(0, len(pitch_chunks[i])): pitch_chunks[i][j][1] *= 2.

        for k in range(len(zero_chunks)): pitch_chunks.insert(zero_chunks[k][0], zero_chunks[k][1])
        pitch = self.recompose_chunks(pitch_chunks=pitch_chunks)
        return pitch

    def correct_jumps(self, pitch):
        for i in range(4, len(pitch) - 6):
            if self.are_close(pitch[i - 4][1], pitch[i - 3][1]) and \
                    self.are_close(pitch[i - 3][1], pitch[i - 2][1]) and \
                    self.are_close(pitch[i - 2][1], pitch[i - 1][1]):

                # quadruple point
                if self.are_close(pitch[i + 4][1], pitch[i + 5][1]) and \
                        self.are_close(pitch[i + 5][1], pitch[i + 6][1]):
                    if not self.are_close(pitch[i][1], pitch[i - 1][1]) and \
                            not self.are_close(pitch[i][1], pitch[i + 4][1]):
                        pitch[i][1] = pitch[i - 1][1]
                    if not self.are_close(pitch[i + 3][1], pitch[i - 1][1]) and \
                            not self.are_close(pitch[i + 3][1], pitch[i + 4][1]):
                        pitch[i + 3][1] = pitch[i + 4][1]

                # triple point
                if self.are_close(pitch[i + 3][1], pitch[i + 4][1]) \
                        and self.are_close(pitch[i + 4][1], pitch[i + 5][1]):
                    if not self.are_close(pitch[i][1], pitch[i - 1][1]) \
                            and not self.are_close(pitch[i][1], pitch[i + 3][1]):
                        pitch[i][1] = pitch[i - 1][1]
                    if not self.are_close(pitch[i + 2][1], pitch[i - 1][1]) and \
                            not self.are_close(pitch[i + 2][1], pitch[i + 3][1]):
                        pitch[i + 2][1] = pitch[i + 3][1]

                # double point
                if self.are_close(pitch[i + 2][1], pitch[i + 3][1]) and \
                        self.are_close(pitch[i + 3][1], pitch[i + 4][1]):
                    if not self.are_close(pitch[i][1], pitch[i - 1][1]) and \
                            not self.are_close(pitch[i][1], pitch[i + 2][1]):
                        pitch[i][1] = pitch[i - 1][1]

                    if not self.are_close(pitch[i + 1][1], pitch[i - 1][1]) and \
                            not self.are_close(pitch[i + 1][1], pitch[i + 2][1]):
                        pitch[i + 1][1] = pitch[i + 2][1]

                # single point
                if self.are_close(pitch[i + 1][1], pitch[i + 2][1]) and \
                        self.are_close(pitch[i + 2][1], pitch[i + 3][1]):
                    if not self.are_close(pitch[i][1], pitch[i - 1][1]) and \
                            not self.are_close(pitch[i][1], pitch[i + 1][1]):
                        pitch[i][1] = pitch[i - 1][1]
        return pitch

    def correct_oct_error(self, pitch):
        pitch_series = [pitch[i][1] for i in range(len(pitch))]
        midf0 = (median(pitch_series) + mean(pitch_series)) / 2

        for i in range(4, len(pitch) - 2):
            # if previous values are continuous
            if self.are_close(pitch[i - 1][1], pitch[i - 2][1]) and \
                    self.are_close(pitch[i - 2][1], pitch[i - 3][1]) and \
                    self.are_close(pitch[i - 3][1], pitch[i - 4][1]):
                if pitch[i][1] > (midf0 * 1.8):
                    if self.are_close(pitch[i - 1][1], pitch[i][1] / 2.):
                        pitch[i][1] /= 2.
                    elif self.are_close(pitch[i - 1][1], pitch[i][1] / 4.):
                        pitch[i][1] /= 4.
                elif pitch[i][1] < (midf0 / 1.8):
                    if self.are_close(pitch[i - 1][1], pitch[i][1] * 2):
                        pitch[i][1] *= 2.
                    elif self.are_close(pitch[i - 1][1], pitch[i][1] * 4):
                        pitch[i][1] *= 4.

        return pitch

    def remove_extreme_values(self, pitch):
        pitch_series = [element[1] for element in pitch]
        pitch_max = max(pitch_series)
        pitch_mean = mean(pitch_series)
        pitch_std = std(pitch_series)

        n = list(histogram(pitch_series, 100))

        for i in range(0, len(n[1]) - 1):
            if n[0][i] == 0 and n[0][i + 1] == 0:
                if sum(n[0][0: i + 1]) > 0.9 * sum(n[0]):
                    pitch_max = (n[1][i] + n[1][i + 1]) / 2.

        pitch_max_cand = max(pitch_mean * 4., pitch_mean + (2 * pitch_std))
        pitch_max = min(pitch_max, pitch_max_cand)

        # max values filter
        for j in range(0, len(pitch)):
            if pitch[j][1] >= pitch_max:
                pitch[j][1] = 0
                pitch[j][2] = 0

        # min values filter
        pitch_min = pitch_mean / 4.
        for j in range(0, len(pitch)):
            if pitch[j][1] <= pitch_min:
                pitch[j][1] = 0
                pitch[j][2] = 0

        return pitch

    def filter_noise_region(self, pitch):
        for i in range(0, 3):

            for j in range(1, len(pitch) - 2):
                if not self.are_close(pitch[i - 1][1], pitch[i][1]) and \
                        self.are_close(pitch[i][1], pitch[i + 1][1]):
                    pitch[i][1] = 0
                    pitch[i][2] = 0

            for j in range(2, len(pitch) - 3):
                if not self.are_close(pitch[j - 2][1], pitch[j][1]) and \
                        not self.are_close(pitch[j - 1][1], pitch[j][1]) and \
                        not self.are_close(pitch[j + 1][1], pitch[j + 2][1]) and \
                        not self.are_close(pitch[j + 1][1], pitch[j + 3][1]):
                    pitch[j][1] = 0
                    pitch[j + 1][1] = 0

        for i in range(1, len(pitch) - 2):
            if not self.are_close(pitch[i - 1][1], pitch[i][1]) and \
                    not self.are_close(pitch[i][1], pitch[i + 1][1]) and \
                    not self.are_close(pitch[i + 1][1], pitch[i + 2][1]) and \
                    not self.are_close(pitch[i - 1][1], pitch[i + 1][1]) and \
                    not self.are_close(pitch[i][1], pitch[i + 2][1]) and \
                    not self.are_close(pitch[i - 1], pitch[i + 2][1]):
                pitch[i][1] = 0
                pitch[i][2] = 0
                pitch[i + 1][1] = 0
                pitch[i + 2][2] = 0

        return pitch

    def filter_chunks_by_energy(self, pitch, chunk_limit):
        pitch_chunks = self.decompose_into_chunks(pitch=pitch, bottom_limit=0.8, upper_limit=1.2)

        chunk_length = [len(element) for element in pitch_chunks]
        longest_chunk = pitch_chunks[chunk_length.index(max(chunk_length))]

        energy = [element[2] for element in longest_chunk]
        min_energy = (sum(energy) / len(energy)) / 6.

        for i in range(0, len(pitch_chunks)):
            temp_energy = [element[2] for element in pitch_chunks[i]]
            ave_energy = sum(temp_energy) / len(temp_energy)

            if ave_energy is not 0:
                if len(pitch_chunks[i]) <= chunk_limit or ave_energy <= min_energy:
                    for element in pitch_chunks[i]:
                        element[1] = 0
                        element[2] = 0
        pitch = self.recompose_chunks(pitch_chunks=pitch_chunks)
        return pitch

    def run(self, pitch):
        for element in pitch:
            if element[1] == 0 or element[1] == 0.: element[1] = 0.

        new_pitch = self.correct_octave_errors_by_chunks(pitch=pitch)
        pitch = self.remove_extreme_values(pitch=new_pitch)

        new_pitch = self.correct_jumps(pitch=pitch)
        new_pitch = list(reversed(new_pitch))
        pitch = self.correct_jumps(pitch=new_pitch)
        pitch = list(reversed(pitch))

        new_pitch = self.filter_noise_region(pitch=pitch)

        pitch = self.correct_oct_error(pitch=new_pitch)
        pitch = list(reversed(pitch))
        new_pitch = self.correct_oct_error(pitch=pitch)
        new_pitch = list(reversed(new_pitch))

        pitch = self.correct_octave_errors_by_chunks(pitch=new_pitch)
        new_pitch = self.filter_chunks_by_energy(pitch=pitch, chunk_limit=self.chunk_limit)

        return new_pitch
