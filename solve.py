import termcolor

words = set(w.upper() for w in open('sowpods.txt').read().split())
words = sorted(words)

values = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
    'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
    'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10,
    '.': 0, '': 0
}
special = {'J', 'Q', 'X', 'Z'}

full_word_tree = {}
for word in words:
    word_tree = full_word_tree
    last = len(word) - 1
    for i, ch in enumerate(word):
        if ch not in word_tree:
            word_tree[ch] = (i == last, {})
        word_tree = word_tree[ch][1]

grid = """
totbaiat
daoia.te
oedvwebu
pyerfutn
ehmuzkln
jafyierx
siclisir
sgomniow
cee.aods
nqahlung
og..ated
pirvlsre
""".strip('\n')

min_lengths = """\
"""

def get(g, x, y):
    """
    Find a character from the original grid.
    """
    try:
        return g[y][x].strip()
    except IndexError:
        return ''

grid = tuple(tuple(l) for l in grid.upper().split('\n'))
min_lengths = tuple(tuple(l) for l in min_lengths.split('\n'))

cx, cy = max(map(len, grid)), len(grid)

grid = dict(((x,y), get(grid, x, y)) for x in range(cx) for y in range(cy))
min_lengths = dict(((x,y), int(get(min_lengths, x, y) or '0')) for x in range(cx) for y in range(cy))

def print_grid(grid, ps=(), removed_tiles=()):
    for y in range(cy):
        print termcolor.colored(str(y).rjust(2), 'grey') + " ",
        for x in range(cx):
            p = x, y
	    if (x, y) in ps:
	        color = 'red'
	    elif (x, y) in removed_tiles:
	        color = 'blue'
	    else:
	        color = None
            print termcolor.colored((grid[p] or ' ') + str(min_lengths[p] or ' '), color),
        print



def surrounding_cells(p):
    """
    Returns co-ordinates for all cells adjacent to the one given.
    """
    x, y = p
    return set(filter(on_board, {
        (x-1, y-1),
        (x-1, y  ),
        (x-1, y+1),
        (x  , y-1),
        (x  , y+1),
        (x+1, y-1),
        (x+1, y  ),
        (x+1, y+1)
    }))

def adjacent_cells(p):
    """
    Returns co-ordinates for all cells adjacent to the one given.
    """
    x, y = p
    return set(filter(on_board, {
        (x-1, y  ),
        (x  , y-1),
        (x  , y+1),
        (x+1, y  ),
    }))

def all_cells():
    return {(x, y) for x in range(cx) for y in range(cy)}

def on_board(p):
    return 0 <= p[0] < cx and 0 <= p[1] < cy

def get_moves(grid, word_tree, used):
    """
    Work out what moves can be made.

    Takes a grid, a partial word tree, and a collection of co-ordinates already
    visited.  Returns [((is_word, word_tree), p)], where p is the co-ordinates
    of a cell for each possible move.
    """
    if used:
        possible = surrounding_cells(used[-1])
    else: # We can start anywhere
        possible = all_cells()

    # Filter out the ones that aren't possible
    possible = {(px, py) for (px, py) in possible
                   if (px, py) not in used and           # Haven't used this letter before
                      grid[(px, py)] in word_tree}       # We're on the way to making an actual word

    return [(word_tree[grid[p]], p) for p in possible]
    
def seek(grid, word, word_tree, used, found, min_length):
    moves = get_moves(grid, word_tree, used)
    for (is_word, new_word_tree), p in moves:
        new_used = used + (p,)
        new_word = word + grid[p]
        new_min_length = max(min_length, min_lengths[p])
        if is_word and len(new_word) >= new_min_length:# and len([1 for x,y in used if x in (7,)]) > 2:
            found.append((new_word, new_used))
        seek(grid, new_word, new_word_tree, new_used, found, new_min_length)

def get_removed_tiles(grid, ps):
    removed = list(ps)
    for i, p in enumerate(ps):
        adjacent = adjacent_cells(p)
        if len(word) < 5:
	    adjacent = set(p for p in adjacent if grid[p] == '.')
	if grid[p] in special:
	    adjacent |= set((px, p[1]) for px in range(0, cx) if px != p[0])

	if i > 0:
	    adjacent.discard(ps[i-1])
	if i < len(word) - 1:
	    adjacent.discard(ps[i+1])
        removed.extend(adjacent)
    return removed

def get_score(grid, ps, removed_tiles):
    return len(ps) * sum(values[grid[r]] for r in removed_tiles)

def get_new_grid(grid, removed):
    new_grid = {}
    for x in range(cx):
        y, oy = cy - 1, cy - 1
	while y >= 0:
	    if (x, oy) not in removed:
		new_grid[(x, y)] = grid.get((x, oy), '')
	        y -= 1
	    oy -= 1
    return new_grid

found = []
seek(grid, '', full_word_tree, (), found, 3)

new_found = []
for word, ps in found:
    removed_tiles = get_removed_tiles(grid, ps)
    score = get_score(grid, ps, removed_tiles)
    new_found.append((word, ps, score, removed_tiles))
found = new_found

#import sys
#found = [f for f in found if f[0]==sys.argv[1].upper()]

found = sorted(found, key=lambda (word, ps, score, removed_tiles): (score, -len(word), word, ps))

#found_words = [(word, ps) for (word, ps) in found_words]

for word, ps, score, removed_tiles in found[-20:]:
    print str(score).rjust(4), word, ps, removed_tiles

from collections import defaultdict
counts = defaultdict(int)
for p in removed_tiles:
    counts[p] += 1

print len(found)

counts = sorted(counts.items(), key=lambda c:c[-1])
print counts

print_grid(grid, ps, removed_tiles)
print
print_grid(get_new_grid(grid, set(removed_tiles)))
