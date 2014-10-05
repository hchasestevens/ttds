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


class Tokens(collections.namedtuple("Vector", 'id_ tokens')):
    def __new__(cls, tokenized_line):
        return super(Tokens, cls).__new__(
            cls,
            tokenized_line[0],
            tokenized_line[1:]
        )

    def __len__(self):
        try:
            return self._len
        except Exception:
            self._len = len(self.tokens)
        return self._len


def tf(word, vector):
    return float(vector.tokens.count(word))


def tokenize(line):
    return re.findall("[A-Za-z0-9]+", line)


def main():
    with open('qrys.txt') as f:
        query_lines = f.readlines()
    with open('docs.txt') as f:
        document_lines = f.readlines()

    queries, documents = [
        [Tokens(tokenize(line.lower())) for line in lines]
        for lines in 
        (query_lines, document_lines)
    ]

    df = collections.defaultdict(float)
    for document in documents:
        for token in set(document.tokens):
            df[token] += 1

    avg_document_len = sum(len(document) for document in documents) / float(len(documents))

    output = []
    k = 2.
    doc_avg_k = k / avg_document_len
    for i, query in enumerate(queries):
        print float(i) / len(queries), '\b'*100,
        for document in documents:
            tfidf_score = 0
            for word in set(query.tokens) & set(document.tokens):
                doc_tf = tf(word, document)

                temp_score = tf(word, query)
                temp_score *= math.log(float(len(documents)) / df[word])
                temp_score *= doc_tf / (doc_tf + (doc_avg_k * len(document)))

                tfidf_score += temp_score
            output.append((query.id_, document.id_, tfidf_score))

    with open(OUTPUT_FNAME, 'w') as f:
        f.write('\n'.join(
            ' 0 '.join(map(str, item)) + ' 0 '
            for item in
            output
        ))


if __name__ == "__main__":
    main()