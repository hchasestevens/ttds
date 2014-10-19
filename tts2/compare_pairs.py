from itertools import izip
f1 = open('pairs.out', 'r').readlines()[:1000]
f2 = open('pairs.ref', 'r').readlines()[:1000]
for l1, l2 in izip(f1, f2):
    if l1 != l2:
        out = ' | '.join(map(lambda x: x.replace('\n', ''), (l1, l2)))
        __ = raw_input(out)

