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


def cos_tfidf(idf_scores, tokens1, tokens2):
    mutual_tokens = set(tokens1) | set(tokens2)
    if not mutual_tokens:
        return 0
    num = []
    q_denom = []  # TODO: probably want to cache these?
    d_denom = []
    for token in mutual_tokens:
        idf = idf_scores[token]
        q = tokens1.count(token) * idf  # TODO: might want these to be stored as dicts 
        d = tokens2.count(token) * idf  # TODO: might want to try to cache these hard.
        num.append(q * d)
        q_denom.append(q ** 2)
        d_denom.append(d ** 2)
    return sum(num) / (sum(q_denom) ** 0.5 * sum(d_denom) ** 0.5) 


def main():
    with open('news.idf', 'r') as f:
        idf_scores = Defaultdict(
            13.6332, 
            ((word, float(val))
             for val, word in 
             (line.split() for line in f.readlines())
             )
        )

    old_stories = []

    with open('news.txt', 'r') as news:
        with open(OUTPUT_FNAME, 'w') as out:
            lines = enumerate(news.readlines())
            for i, line in lines:
                print i
                new_story = [token.lower() for token in line.split()[1:]]
                try:
                    best_score, best_match = max(
                        (cos_tfidf(idf_scores, new_story, old_story), -j)
                        for j, old_story in
                        enumerate(old_stories)
                    )
                    if best_score > THRESHOLD:
                        out.write(str(i + 1) + " " + str(-best_match + 1) + "\n")  # not sure this is most efficient string construction
                        out.flush()
                except ValueError:
                    pass  # TODO: more elegant/less overhead way to do this?
                finally:
                    old_stories.append(new_story)


if __name__ == '__main__':
    main()

