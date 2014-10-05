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
import re
import itertools
import math
from nltk.corpus import stopwords
STOPWORDS = stopwords.words('english')


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


def ngrams(n, list_, delimiter=''):
    streams = (list_[i:] for i in xrange(n))
    return [delimiter.join(ngram) for ngram in itertools.izip(*streams)]


def tf(word, vector):
    return float(vector.tokens.count(word))


def tokenize(line):
    base_tokens = [
        token
        for token in 
        re.findall("[A-Za-z0-9]+", line)
    ]
    tokens = [
        token
        for token in 
        base_tokens
        if not token in STOPWORDS
    ]
    morpheme_4grams = itertools.chain(*[
        ngrams(4, token)
        for token in
        tokens
    ])
    word_bigrams = ngrams(2, tokens, '|')
    extended_tokens = [
        token
        for token in
        re.findall("[A-Za-z0-9\.\-\_\/]+", line)
        if not token in tokens
    ]
    stripped_extended_tokens = [
        ''.join(re.findall("[A-Za-z0-9]+", token))
        for token in
        extended_tokens
    ]
    tokens.extend(morpheme_4grams)
    tokens.extend(word_bigrams)
    tokens.extend(extended_tokens)
    tokens.extend(stripped_extended_tokens)
    return tokens


def main(query_fname, output_fname):
    with open(query_fname) as f:
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

    with open(output_fname, 'w') as f:
        f.write('\n'.join(
            ' 0 '.join(map(str, item)) + ' 0 '
            for item in
            output
        ))


if __name__ == "__main__":
    main('qrys.txt', 'best.top')
    print
    main('test.txt', 'test.top')