pitch-post-filter
===========

Introduction
------------
Repository for post-processing pitch tracks to filter erroneous estimations and correct octave errors.

This repository implements the post-filtering methodology explained in _Bozkurt, B. (2008)_

Given a pitch track, the algorithm:
- corrects octave errors
- removes noisy regions
- removes small chunks
- removes extremely high or low pitch estimations

Usage
=======

Installation
============

If you want to install pitch-post-filter, it is recommended to install the repository and its dependencies into a virtualenv. 

In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install compmusic like this instead

    pip install -e .

Now you can install the rest of the dependencies:

    pip install -r requirements

Author
-------
Hasan Sercan Atlı <hsercanatli AT gmail DOT com>

Contributors
-------
Sertan Şentürk (packaging) <contact AT sertansenturk DOT com>

References
-------
Bozkurt, B. (2008). An automatic pitch analysis method for turkish maqam music. Journal of New Music Research, 37(1), 1-13.