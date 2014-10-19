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


def cycle(values):
    """Reimplementation of itertools.cycle"""
    while True:
        for value in values:
            yield value


def counter_idf(tokens, get_idf):
    """Pseudo-reimplementation of collections.Counter"""
    d = {}
    for token in tokens:
        try:
            d[token] += get_idf(token, 13.6332)
        except KeyError:
            d[token] = get_idf(token, 13.6332)
    return d


def indexed_cos_tfidf(get_idf, q_tokens, q_denom, token_index, d_denoms):
    doc_scores = {}
    for token, count in q_tokens.iteritems():
        try:
            doc_counts = token_index[token]
        except KeyError:
            continue
        for doc, doc_count in doc_counts:
            try:
                doc_scores[doc] += count * doc_count
            except KeyError:
                doc_scores[doc] = count * doc_count
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
    get_idf = idf_scores.get

    english_stopwords = set((
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
        'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
        'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who'
        , 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 
        'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 
        'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 
        'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 
        'about', 'against', 'between', 'into', 'through', 'during', 'before', 
        'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 
        'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
        'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 
        'can', 'will', 'just', 'don', 'should', 'now'
    ))  # taken from nltk.corpus.stopwords.words('english')

    news_stopwords = set(word for word, value in idf_scores.iteritems() if value < 3.4951)

    stopwords = frozenset(english_stopwords | news_stopwords)
    in_stopwords = stopwords.__contains__

    old_denoms = {}
    token_index = {}

    global N

    #doline = cycle(range(15))

    with open('news.txt', 'r') as news:
        with open(OUTPUT_FNAME, 'w') as out:
            out_write = out.write
            out_flush = out.flush
            lines = enumerate(news)
            for i, line in lines:
                if i == N:  # TODO: probably want to izip with xrange or something?
                    break
                if i % 100 == 0:  # TODO: remove
                    print i
                new_story = counter_idf((token for token in line.lower().split()[1:] if not in_stopwords(token)), get_idf)
                new_story_denom = sum(v ** 2 for k, v in new_story.iteritems()) ** 0.5
                try:
                    #if next(doline):
                    best_match, best_score = indexed_cos_tfidf(get_idf, new_story, new_story_denom, token_index, old_denoms)
                    if best_score > THRESHOLD:
                        out_write(str(i + 1) + " " + str(-best_match + 1) + "\n")  # not sure this is most efficient string construction
                        out_flush()
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
