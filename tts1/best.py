"""
Try to improve the accuracy of your retrieval algorithms. You are free to use
any techniques that you think may improve retrieval effectiveness, subject to
the restrictions. Use average precision (see task 4) to judge the accuracy of
your approach. Save your most successful algorithm as best.py. Output the
results to a file called best.top. Come up with a short distinctive name for
your algorithm and save it in a file called best.id. This name will be used
when we report the effectiveness of your algorithm.
...
Run your most successful algorithm (best.py) on the testing queries in
test.txt. Output the results to a file called test.top. Average precision (MAP)
on these testing queries will be used as the main criterion for marking this
task. You cannot compute MAP yourself (we are not providing relevance
judgements for the test set), but assume that MAP for the training queries will
be representative of the MAP for the testing queries.
"""
import collections
import functools
import re
import itertools
import math
from nltk.corpus import stopwords


OUTPUT_FNAME = "best.top"


def cached_by_func(func, f):
    cache = {}
    def new_f(*args, **kwargs):
        key = tuple(map(func, args)), tuple(map(func, kwargs))
        result = cache.get(key)
        if result is None:
            result = f(*args, **kwargs)
            cache[key] = result
        return result
    return new_f

cached_by_id = functools.partial(cached_by_func, id)
cached_by_value = functools.partial(cached_by_func, lambda x: x)


def counter(tokens):
    d = collections.defaultdict(float)
    for token in tokens:
        d[token] += 1
    return d


class Vector(collections.namedtuple("Vector", 'id_ vector')):
    def __new__(cls, tokenized_line):
        return super(Vector, cls).__new__(
            cls,
            tokenized_line[0],
            tokenized_line[1:]
        )

    def __len__(self):
        try:
            return self._len
        except Exception:
            self._len = len(self.vector)
        return self._len

    def idf(self, dtf, doc_avg_k, num_docs, df, word):
        try:
            return self._idf
        except Exception:
            self._idf = (dtf / (dtf + (doc_avg_k * len(self)))) * math.log(num_docs / df(word))
        return self._idf


def tf(word, vector):
    return float(vector.vector.count(word))


def df_factory(collection):
    @cached_by_value
    def df(word):
        return float(sum(
            document.vector.count(word)
            for document in
            collection
        ))
    return df


def ngrams(n, word):
    if len(word) <= n:
        return word
    return zip(*[word[i:] for i in xrange(n)])


def tf_idf_factory(df, avg_doclen, num_docs):
    k = 2.
    doc_avg_k = k / avg_doclen
    stops = stopwords.words('english')
    def tf_idf(query, document):
        return sum(
            tf(ngram, query) * document.idf(tf(ngram, document), doc_avg_k, num_docs, df, word)
            for word in
            set(query.vector) | set(document.vector)
            for ngram in 
            itertools.chain(ngrams(3, word), ngrams(4, word), [word])
            if word not in stops
        )
    return tf_idf


def main():
    with open('qrys.txt') as f:
        queries = f.readlines()
    with open('docs.txt') as f:
        documents = f.readlines()

    tokenizer = functools.partial(re.findall, "[A-Za-z0-9]+")
    queries, documents = [
        [Vector(tokenizer(line.lower())) for line in lines]
        for lines in 
        (queries, documents)
    ]

    df = df_factory(documents)

    avg_document_len = sum(len(document) for document in documents) / float(len(documents))

    tf_idf = tf_idf_factory(df, avg_document_len, len(documents))

    output = (
        (query.id_,
         document.id_,
         tf_idf(query, document)
        )
        for query in 
        queries
        for document in 
        documents
    )

    output_ = []
    for i, item in enumerate(output):
        print float(i) / (len(queries) * len(documents)), '\b'*100,
        output_.append(item)
    output = output_

    with open(OUTPUT_FNAME, 'w') as f:
        f.write('\n'.join(
            ' 0 '.join(map(str, item)) + ' 0 '
            for item in
            output
        ))


if __name__ == "__main__":
    main()
