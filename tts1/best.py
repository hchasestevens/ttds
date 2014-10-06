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
import copy
from nltk.corpus import stopwords
import operator
import functools
import time
STOPWORDS = stopwords.words('english')


class Tokens(collections.namedtuple("Vector", 'id_ tokens base_tokens')):
    def __new__(cls, line, synonyms=None):
        base_tokens = Tokens.base_tokenize(line)
        return super(Tokens, cls).__new__(
            cls,
            base_tokens[0],
            Tokens.tokenize(line, synonyms),
            base_tokens[1:]
        )

    @staticmethod
    def base_tokenize(line):
        return [
            token
            for token in 
            re.findall("[A-Za-z0-9]+", line)
        ]

    @staticmethod
    def tokenize(line, synonyms=None):
        base_tokens = Tokens.base_tokenize(line)
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
        synonymous_tokens = []
        if synonyms is not None:
            for token in tokens:
                synonymous_tokens.extend(synonyms.get(token, []))
        tokens.extend(morpheme_4grams)
        tokens.extend(word_bigrams)
        tokens.extend(extended_tokens)
        tokens.extend(synonymous_tokens)
        return tokens

    def __len__(self):
        try:
            return self._len
        except Exception:
            self._len = len(self.tokens)
        return self._len

    def __contains__(self, token):
        return token in self.tokens

    def __hash__(self):
        return int(self.id_)


def ngrams(n, list_, delimiter=''):
    streams = (list_[i:] for i in xrange(n))
    return [delimiter.join(ngram) for ngram in itertools.izip(*streams)]


def tf(word, vector):
    return float(vector.tokens.count(word))


def tokenize(line, query=False):
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
    tokens.extend(morpheme_4grams)
    tokens.extend(word_bigrams)
    tokens.extend(extended_tokens)
    if query:
        pass
    return tokens


def main(query_fname, output_fname):
    with open(query_fname) as f:
        query_lines = f.readlines()
    with open('docs.txt') as f:
        document_lines = f.readlines()

    print "Tokenizing documents"
    documents = [
        Tokens(line.lower())
        for line in 
        document_lines
    ]

    print "Calculating DFs"
    df = collections.defaultdict(float)
    for document in documents:
        for token in set(document.tokens):
            df[token] += 1

    print "Populating synonyms"
    common_tokens = frozenset(
        token 
        for document in documents 
        for token in document.base_tokens
        if (len(documents) / 10.) > df[token] > (len(documents) / 150.)
        and token not in STOPWORDS
        and len(token) > 4
    )
    print len(common_tokens)
    expected_mi = collections.defaultdict(float)
    i = 0
    fact = lambda x: reduce(operator.mul, range(1, x+1))
    total = fact(len(common_tokens)) / fact(len(common_tokens) - 2) / fact(2)
    print total
    for token_a, token_b in itertools.combinations(common_tokens, 2):
        i += 1
        print float(i) / total, '\b'*100,
        if token_a in token_b or token_b in token_a: continue
        key = tuple(sorted((token_a, token_b)))
        n_ab = 0
        for document in documents:
            n_ab += token_a in document and token_b in document
        try:
            expected_mi[key] = n_ab * math.log(len(common_tokens) * (n_ab / (df[token_a] * df[token_b])))
        except ValueError:
            expected_mi[key] = 0.
    average_expected_mi = float(sum(v for v in expected_mi.itervalues())) / len(expected_mi)
    expected_mi_stdev = math.sqrt(
        float(
            sum(
                (v - average_expected_mi) ** 2 
                for v in expected_mi.itervalues()
            ) 
        )
        / len(expected_mi)
    )
    synonym_pairs = [k for k, v in expected_mi.iteritems() if v > (average_expected_mi + 2*expected_mi_stdev)]
    if not synonym_pairs:
        synonym_pairs = [k for k, v in expected_mi.iteritems() if v > (average_expected_mi + 1.5*expected_mi_stdev)]
        print 'Used 1.5 stdevs'
    if not synonym_pairs:
        synonym_pairs = [k for k, v in expected_mi.iteritems() if v > (average_expected_mi + 1*expected_mi_stdev)]
        print 'Used 1 stdev'
    print average_expected_mi, expected_mi_stdev
    print synonym_pairs
    synonyms = collections.defaultdict(set)
    for a, b in synonym_pairs:
        synonyms[a].add(b)
        synonyms[b].add(a)

    print "Tokenizing queries"
    queries = [
        Tokens(line.lower(), synonyms)
        for line in 
        query_lines
    ]

    avg_document_len = sum(len(document) for document in documents) / float(len(documents))

    print "Performing IR"
    output = []
    k = 2.
    doc_avg_k = k / avg_document_len
    for i, query in enumerate(queries):
        print float(i) / len(queries), '\b'*100,
        query_scores = {}
        query_tokens = frozenset(query.tokens)
        for document in documents:
            tfidf_score = 0
            for word in query_tokens & set(document.tokens):
                doc_tf = tf(word, document)

                temp_score = tf(word, query)
                temp_score *= math.log(float(len(documents)) / df[word])
                temp_score *= doc_tf / (doc_tf + (doc_avg_k * len(document)))

                tfidf_score += temp_score
            query_scores[document] = tfidf_score

        for document in documents:
            output.append((query.id_, document.id_, query_scores[document]))

    with open(output_fname, 'w') as f:
        f.write('\n'.join(
            ' 0 '.join(map(str, item)) + ' 0 '
            for item in
            output
        ))


if __name__ == "__main__":
    main('qrys.txt', 'best.top')
    print
    t1 = time.time()
    main('test.txt', 'test.top')
    print
    print (time.time() - t1) / 60.