"""
Algorithm: 
for each story A in news.txt: 
   find the most similar story B that came before A 
   if similarity(A,B) > threshold: 
     output pair: A,B

You also make the following initial design decisions (required for tasks 1 and 2):

tokenise each story by splitting on whitespace
lowercase the tokens, but do not stem them, and do not remove stopwords
use tf-idf weighted cosine for measuring the similarity of two stories
do not squash term frequencies: use tf instead of tf/(tf+K)
load idf values from news.idf, set idf=13.6332 for any word not in news.idf
set the threshold to 0.2 for tasks 1 and 2
when similarity(A,B1) = similarity(A,B2) pick the earlier story as a pair

...

Implement a brute-force version of the Algorithm, without any indexing. 
Your code for step 2 of the Algorithm should look something like this: 
   B = 1 
   for i = 2..A-1: 
     if cosine(A,i) > cosine(A,B): 
       B = i 
Your implementation (brute.py) should read the news stories line-by-line 
from news.txt in the current directory and write the results to pairs.out 
in the current directory. Stop after processing 10,000 stories.
"""

OUTPUT_FNAME = 'pairs.out'
THRESHOLD = 0.2


class Defaultdict(dict):
    """Pseudo-reimplementation of collections.defaultdict"""
    def __init__(self, default_value, *args, **kwargs):
        self._default_value = default_value
        super(Defaultdict, self).__init__(*args, **kwargs)

    def __getitem__(self, item):
        try:
            return super(Defaultdict, self).__getitem__(item)
        except KeyError:
            return self._default_value


def take(n, iterable):
    iterable_ = iter(iterable)
    for __ in xrange(n):
        yield next(iterable)


def main():
    with open('news.txt', 'r') as f:
        news_lines = (line.split() for line in f.readlines())

    news_items = [
        [token.lower() for token in tokens[1:]]
        for tokens in 
        news_lines
    ]

    with open('news.idf', 'r') as f:
        idf_scores = Defaultdict(
            13.6332, 
            ((word, float(val))
             for val, word in 
             (line.split() for line in f.readlines())
             )
        )

    out_pairs = []

    for i, primary_tokens in enumerate(news_items):
        best_match = None
        best_score = 0
        for j, secondary_tokens in enumerate(news_items):
            if i == j:
                break
            # do similarity calculations
        if best_score > THRESHOLD:
            out_pairs.append((i + 1, j + 1))


if __name__ == '__main__':
    main()

