import collections
import itertools

import termcolor

State = collections.namedtuple('State', ('grid', 'score', 'used', 'cx', 'cy'))
Cell = collections.namedtuple('Cell', ('letter', 'min'))
WordTree = collections.namedtuple('WordTree', ('is_word', 'children'))
Candidate = collections.namedtuple('Candidate', ('word', 'ps', 'removed', 'score'))

words = set(w.upper() for w in open('sowpods.txt').read().split())
words = sorted(words)
full_word_tree = {}
for word in words:
    word_tree = full_word_tree
    last = len(word) - 1
    for i, ch in enumerate(word):
        if ch not in word_tree:
            word_tree[ch] = WordTree(i == last, {})
        word_tree = word_tree[ch].children

values = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
    'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
    'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10,
    '.': 0, '': 0
}
special = {'J', 'Q', 'X', 'Z'}

grid = """
       d
       y
       f
       a
       o
o      i
t      o
n      o
o b  o j
uftawrlo
igwnlahl
""".strip('\n')

mins = """\
"""

def state_from_text(letters, mins='', score=0, used=()):
    grid = {}
    cs = {y: {x: c for x, c in enumerate(row)} for y, row in enumerate(letters.upper().split('\n'))}
    ms = {y: {x: c for x, c in enumerate(row)} for y, row in enumerate(mins.split('\n'))}
    cx, cy = max(map(len, cs.values())), len(cs)
    print cx, cy
    for x in range(cx):
        for y in range(cy):
	    c = cs[y].get(x, '').strip()
	    m = int(ms.get(y, {}).get(x, 0))
	    grid[(x, y)] = Cell(c, m)
    return State(grid, score, used, cx, cy)

state = state_from_text(grid, mins)


def print_state(state, candidate=None):
    for y in range(state.cy):
        print termcolor.colored(str(y).rjust(2), 'grey') + " ",
        for x in range(state.cx):
            p = x, y
	    if candidate and (x, y) in candidate.ps:
	        color = 'red'
	    elif candidate and (x, y) in candidate.removed:
	        color = 'blue'
	    else:
	        color = None
	    cell = state.grid[p]
            print termcolor.colored((cell.letter or ' ') + str(cell.min or ' '), color),
        print



def surrounding_cells(state, p):
    """
    Returns co-ordinates for all cells adjacent to the one given.
    """
    x, y = p
    return set(p for p in {
        (x-1, y-1),
        (x-1, y  ),
        (x-1, y+1),
        (x  , y-1),
        (x  , y+1),
        (x+1, y-1),
        (x+1, y  ),
        (x+1, y+1)
    } if on_board(state, p))

def adjacent_cells(state, p):
    """
    Returns co-ordinates for all cells adjacent to the one given.
    """
    x, y = p
    return set(p for p in {
        (x-1, y  ),
        (x  , y-1),
        (x  , y+1),
        (x+1, y  ),
    } if on_board(state, p))

def all_cells(state):
    return {(x, y) for x in range(state.cx) for y in range(state.cy)}

def on_board(state, p):
    return 0 <= p[0] < state.cx and 0 <= p[1] < state.cy

def get_moves(state, word_tree, visited):
    """
    Work out what moves can be made.

    Takes a grid, a partial word tree, and a collection of co-ordinates already
    visited.  Returns [((is_word, word_tree), p)], where p is the co-ordinates
    of a cell for each possible move.
    """
    if visited:
        possible = surrounding_cells(state, visited[-1])
    else: # We can start anywhere
        possible = all_cells(state)

    # Filter out the ones that aren't possible
    possible = {(px, py) for (px, py) in possible
                   if (px, py) not in visited and          # Haven't used this letter before
                      state.grid[(px, py)].letter in word_tree}   # We're on the way to making an actual word

    return [(word_tree[state.grid[p].letter], p) for p in possible]
    
def seek(state, candidates, word_tree=full_word_tree, word='', min_length=3, visited=()):
    moves = get_moves(state, word_tree, visited)
    for (is_word, new_word_tree), p in moves:
        new_visited = visited + (p,)
        new_word = word + state.grid[p].letter
        new_min_length = max(min_length, state.grid[p].min)
        if is_word and len(new_word) >= new_min_length and new_word not in state.used:
	    removed_tiles = get_removed_tiles(state, new_word, new_visited)
	    score =  get_score(state, new_visited, removed_tiles)
	    candidates.append(Candidate(new_word, new_visited, frozenset(removed_tiles), score))
        seek(state, candidates, new_word_tree, new_word, new_min_length, new_visited)

def get_removed_tiles(state, word, ps):
    removed = list(ps)
    for i, p in enumerate(ps):
        adjacent = adjacent_cells(state, p)
        if len(word) < 5:
	    adjacent = set(p for p in adjacent if state.grid[p].letter == '.')
	if state.grid[p].letter in special:
	    adjacent |= set((px, p[1]) for px in range(0, state.cx) if px != p[0])

	if i > 0:
	    adjacent.discard(ps[i-1])
	if i < len(word) - 1:
	    adjacent.discard(ps[i+1])
        removed.extend(adjacent)
    return removed

def get_score(state, ps, removed_tiles):
    return len(ps) * sum(values[state.grid[r].letter] for r in removed_tiles)

def get_new_grid(state, candidate):
    new_grid = {}
    for x in range(state.cx):
        y, oy = state.cy - 1, state.cy - 1
	while y >= 0:
	    if (x, oy) not in candidate.removed:
		new_grid[(x, y)] = state.grid.get((x, oy), Cell('', 0))
	        y -= 1
	    oy -= 1
    return State(new_grid,
                 state.score + candidate.score,
		 state.used + (candidate.word,),
		 state.cx, state.cy)

candidates = []
seek(state, candidates) 

candidates.sort(key=lambda c: (c.score, -len(c.word), c.word))

for candidate in candidates[-20:]:
    print str(candidate.score).rjust(4), candidate.word

print len(candidates)

print_state(state)
print
print_state(state, candidates[-1])
print
print_state(get_new_grid(state, candidates[-1])

