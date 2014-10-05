"""
Implement a tf.idf retrieval algorithm (tfidf.py), based on the weighted sum
formula with tf.idf weighting (lecture 3). Set k=2. All relevant statistics
should be computed from docs.txt. Tokenize exactly as in task 1. Save the
results in a file called tfidf.top.
"""
import collections
import functools
import re
import itertools
import math


OUTPUT_FNAME = "tfidf.top"


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
            self._idf = (float(dtf) / (dtf + (doc_avg_k * len(self)))) * math.log(float(num_docs) / df(word))
        return self._idf


def tf(word, vector):
    return float(vector.vector.count(word))


def df_factory(collection):
    @cached_by_value
    def df(word):
        return float(sum(
            word in document.vector
            for document in
            collection
        ))
    return df


def tf_idf_factory(df, avg_doclen, num_docs):
    k = 2.
    doc_avg_k = k / avg_doclen
    def tf_idf(query, document):
        return sum(
            tf(word, query) * document.idf(tf(word, document), doc_avg_k, num_docs, df, word)
            for word in
            set(query.vector) | set(document.vector)
        )
    return tf_idf


def main():
    with open('qrys.txt') as f:
        query_lines = f.readlines()
    with open('docs.txt') as f:
        document_lines = f.readlines()

    tokenizer = functools.partial(re.findall, "[A-Za-z0-9]+")
    queries, documents = [
        [Vector(tokenizer(line.lower())) for line in lines]
        for lines in 
        (query_lines, document_lines)
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