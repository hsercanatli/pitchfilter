pitchfilter
===========

Repository for post-processing pitch tracks to filter erroneous estimations and correct octave errors.

Introduction
------------
This repository implements the post-filtering methodology explained in _Bozkurt, B. (2008)_.

Given a pitch track, the algorithm:
- corrects octave errors
- removes noisy regions
- removes small chunks
- removes extremely high or low pitch estimations

Usage
-------
The method accepts numpy arrays, where the first column holds the time stamps (in seconds), the second column holds the frequencies (in Hz) and the third column holds the pitch saliences/confidence.

In the following example, the algorithm filters the pitch track of [feda89e3-a50d-4ff8-87d4-c1e531cc1233](http://musicbrainz.org/recording/feda89e3-a50d-4ff8-87d4-c1e531cc1233) extracted using [Predominant Melody Extractor](https://github.com/sertansenturk/predominantmelodymakam) repository.

```python
import json
from pitchfilter.PitchFilter import PitchFilter
import numpy

# reading extracted pitch from json
pitch = numpy.array(json.load(open("sample_data/feda89e3-a50d-4ff8-87d4-c1e531cc1233.json", 'r'))['pitch'])

# filtering the extracted pitch
flt = PitchFilter()
pitch_filt = flt.run(pitch)
```

Installation
-------

If you want to install pitchfilter, it is recommended to install the repository and its dependencies into a virtualenv. 

In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then install the package like this instead:

    pip install -e .

Authors
-------
Hasan Sercan Atlı	hsercanatli@gmail.com  
Sertan Senturk		contact@sertansenturk.com

References
-------
Bozkurt, B. (2008). An automatic pitch analysis method for turkish maqam music. Journal of New Music Research, 37(1), 1-13.
