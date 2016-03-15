import os
from musicxmlconverter.symbtr2musicxml import SymbTrScore


def test_pitch_filter():
    pitch = json.load(open("sample_data/feda89e3-a50d-4ff8-87d4-c1e531cc1233"
                           ".json", 'r'))['pitch']

    # filtering the extracted pitch
    flt = PitchFilter()
    pitch_filt = flt.run(pitch)

    
    assert savedxmlstr == xmlstr
