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

OUTPUT_FNAME = 'pairs.out.best'
THRESHOLD = 0.2


def counter(tokens):
    """Pseudo-reimplementation of collections.Counter"""
    d = {}
    for token in tokens:
        try:
            d[token] += 1
        except KeyError:
            d[token] = 1
    return d


def indexed_cos_tfidf(idf_scores, q_tokens, q_denom, token_index, d_denoms):
    doc_scores = {}
    for token, count in q_tokens.iteritems():
        try:
            doc_counts = token_index[token]
        except KeyError:
            continue
        idf = idf_scores.get(token, 13.6332)
        q = count * idf  
        for doc, doc_count in doc_counts:
            try:
                doc_scores[doc] += q * doc_count * idf
            except KeyError:
                doc_scores[doc] = q * doc_count * idf
    score, doc = max(
        (score / (q_denom * d_denoms[doc]), -doc)
        for doc, score in
        doc_scores.iteritems()
    )
    return doc, score

N = 10000

def main():
    with open('news.idf', 'r') as f:
        idf_scores = dict(
            ((word, float(val))
             for val, word in 
             (line.split() for line in f)
             )
        )

    old_denoms = {}
    token_index = {}

    global N

    with open('news.txt', 'r') as news:
        with open(OUTPUT_FNAME, 'w') as out:
            lines = enumerate(news)
            for i, line in lines:
                if i == N:  # TODO: probably want to izip with xrange or something?
                    break
                if i % 100 == 0:  # TODO: remove
                    print i
                new_story = counter(token.lower() for token in line.split()[1:])
                new_story_denom = sum((v * idf_scores.get(k, 13.6332)) ** 2 for k, v in new_story.iteritems()) ** 0.5
                try:
                    best_match, best_score = indexed_cos_tfidf(idf_scores, new_story, new_story_denom, token_index, old_denoms)
                    if best_score > THRESHOLD:
                        out.write(str(i + 1) + " " + str(-best_match + 1) + "\n")  # not sure this is most efficient string construction
                        out.flush()
                except ValueError:
                    pass  # TODO: more elegant/less overhead way to do this?
                finally:
                    for token, count in new_story.iteritems():
                        try:
                            token_index[token].append((i, count))
                        except KeyError:
                            token_index[token] = [(i, count)]
                    old_denoms[i] = new_story_denom


if __name__ == '__main__':
    import time; print "WARNING: IMPORT STILL IN FILE"  # TODO: remove
    t = time.time()
    main()
    print (time.time() - t) / 60.
    print 'best'
    print N
