import os
import numpy
import json
from pitchfilter.PitchFilter import PitchFilter

def test_pitch_filter():
    # reading extracted pitch from json
    pitch = numpy.array(json.load(open(os.path.join("sample_data",
                     "e72db0ad-2ed9-467b-88ae-1f91edcd2c59.json"), 'r')))

    # filtering the extracted pitch
    flt = PitchFilter()
    pitch_filt = flt.run(pitch)

    saved_filt = numpy.array(json.load(open(os.path.join(
        "sample_data", "e72db0ad-2ed9-467b-88ae-1f91edcd2c59_filtered.json"),
        'r')))

    assert numpy.allclose(saved_filt, pitch_filt)
