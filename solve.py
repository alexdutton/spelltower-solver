words = set(w.upper() for w in open('/usr/share/dict/words').read().split())

swords = sorted(words)

full_word_tree = {}

for sword in swords:
    word_tree = full_word_tree
    last = len(sword) - 1
    for i, ch in enumerate(sword):
        if ch not in word_tree:
            word_tree[ch] = (i == last, {})
        word_tree = word_tree[ch][1]

grid = """\
u      t
oa    ep
lr    l.
oz   uve
tsa isfe
.fs.waib
iormdaio
qndcojne 
yn.iseae
gitygaro
dtestika
exac.miw
"""

min_lengths = """\












"""

def get(g, x, y):
    try:
        return g[y][x].strip()
    except IndexError:
        return ''

grid = tuple(tuple(l) for l in grid.upper().split('\n'))
min_lengths = tuple(tuple(l) for l in min_lengths.split('\n'))

cx, cy = max(map(len, grid)), len(grid)

grid = dict(((x,y), get(grid, x, y)) for x in range(cx) for y in range(cy))
min_lengths = dict(((x,y), int(get(min_lengths, x, y) or '0')) for x in range(cx) for y in range(cy))

for y in range(cy):
    for x in range(cx):
        p = x, y
        print (grid[p] or ' ') + str(min_lengths[p] or ' '),
    print


used = frozenset()

def get_moves(grid, word_tree, used):
    x, y = used[-1]
    possible = {
        (x-1, y-1),
        (x-1, y  ),
        (x-1, y+1),
        (x  , y-1),
        (x  , y+1),
        (x+1, y-1),
        (x+1, y  ),
        (x+1, y+1)
    }
    for px, py in possible:
        if not (0 <= px < cx and 0 <= py < cy):
            continue
    possible = {(px, py) for (px, py) in possible
                   if (px, py) not in used and           # Haven't used this letter before
                      0 <= px < cx and 0 <= py < cy and  # Haven't strayed outside the grid
                      grid[(px, py)] in word_tree}       # We're on the way to making an actual word

    return [(word_tree[grid[p]], p) for p in possible]
    
    

def seek(grid, word, word_tree, used, found, min_length):
    moves = get_moves(grid, word_tree, used)
    for (is_word, new_word_tree), p in moves:
        new_used = used + (p,)
        new_word = word + grid[p]
        new_min_length = max(min_length, min_lengths[p])
        if is_word and len(new_word) >= new_min_length:
            found.add(new_word)
        seek(grid, new_word, new_word_tree, new_used, found, new_min_length)

found = set()
for x in range(cx):
    for y in range(cy):
        p = x, y
        word = grid[p]
        try:
            word_tree = full_word_tree[word][1]
        except KeyError:
            continue
        else:
            min_length = max(min_lengths[p], 3)
            seek(grid, word, word_tree, (p,), found, min_length)

print '\n'.join(sorted(found, key=lambda w: (len(w), w)))


