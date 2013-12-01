A SpellTower solver
===================

A very simple and hacky solver for SpellTower.

To use it, edit the ``grid`` variable in ``solver.py``. Use spaces for empty tiles, and ``'.'`` for solid blanks. If you care about minimum word lengths, edit the ``min_lengths`` variable to contain digits that correspond to the letters in ``grid``.

It's hard-coded to use ``/usr/share/dict/words`` on Linux; it suggests lots of words that SpellTower doesn't accept.

If you want to put a nicer interface on it I'd be rather grateful!


License
-------

This code is in the public domain. Feel free to do with it as you please, though if you find it useful I'd be interested to hear from you.


How it works
------------

First it builds a tree of words from ``/usr/share/dict/words``. The tree is contained in a ``dict``, where the keys are letters, and the values are pairs of "is this a word?" and the remainder of the tree. Thus::

   full_word_tree['h']['e'] == (True, {...})        # 'HE' is a word
   full_word_tree['h']['e']['l'] == (False, {...})  # 'HEL' isn't a word
   full_word_tree['x']['p'] -> KeyError             # No words start 'XP'

The script goes through every starting square and does a depth-first search of paths that match words in the tree. If the first part of the pair is ``True``, we add it to the list of words we've found.


Possible extensions
-------------------

* work out what the resulting grid would be
* calculate scores
* add a metric to prefer strategic plays (e.g. keeping the edges low)
* a better way of inputting the initial grid
* comments!

