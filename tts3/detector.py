"""
TASKS  

Have a look at the training set and identify the kind of plagiarism
Alpine Dale denoted as type 1 and type 2.  

Implement a detection tool able to
spot plagiarism of type 1.  Check the correctness of your implementation by
comparing it to the provided truth (type1.truth) on the training data set.

Implement or extend your detection tool to also handle plagiarism of type 2.
Use the the truth (type2.truth) on the training data set to tune your
algorithm.  

Run your plagiarism detector on the test dataset (data.test) for
30 minutes and save all detected cases of plagiarism in their adequate output
files.  It is your responisbility to ensure that the output is stored even if
the program is terminated after 30 minutes.  

Adapt Finn's method (set c = 100)
to extract all areas with high number densities from the provided finn data
set (data.finn).  Then investigate those areas for possible plagiarism of type
1 or 2.  Note that any case of plagiarism will consist of at least a couple of
tokens.  

Provide a detailed overview of the decisions you made in designing
your plagiarism detection tool.  Explain your thought process and outline the
conclusion you drew.  In particular explain, what kinds of plagiarism you have
detected and how?  Please note: The report should not be a step-by-step
walkthrough of your code Don't waste space explaining implementation details
like program structure, classes, functions, etc.  Describe what you tried, why
you tried it, how it improved results, etc.
"""
import hashlib
import re
from collections import defaultdict
import itertools

from nltk.corpus import stopwords

INPUT_FNAME = "data.test"
OUTPUT_FNAMES = (
    "type{0}.dup".format(n + 1)
    for n in 
    xrange(3)
)
TOKENIZATION_REGEX = r'''[\t\r\n\\~`!@#$%^&*()_\-+=[\]{}|:;"'<>,.?/\s]+'''
STOPWORDS = frozenset(stopwords.words('english'))
L = 1
K = 28


def counter(tokens):
    """Psuedo-reimplementation of collections.Counter"""
    d = defaultdict(int)
    for token in tokens:
        d[token] += 1
    return d


def exhaust(gen):  # may want to replace with with list comp w/o assignment
    for item in gen:
        pass


def output(*args):
    return "{0} {1}\n".format(*sorted(args))


def chunks(chunk_size, token):
    assert not len(token) % chunk_size
    return itertools.izip(*[token[x::chunk_size] for x in xrange(chunk_size)])


def num_differences(set_a, set_b):
    return len(set_a | set_b) - len(set_a & set_b)


def finn(tokens):
    characterization = (token.isdigit() for token in tokens)
    c = 100
    best_score = 0
    best_subseq = []
    current_score = 0
    current_subseq = []
    for token, is_digit in itertools.izip(tokens, characterization):
        if not is_digit:
            current_score = max(current_score - 1, 0)
            if not current_score:
                current_subseq = []
            else:
                current_subseq.append(token)
            continue
        current_score += c
        current_subseq.append(token)
        if current_score > best_score:
            best_score, best_subseq = current_score, current_subseq[:]
    return best_subseq or tokens


def main(t):
    type_1s = {}
    type_2s = [defaultdict(list) for __ in xrange(L)]
    with open(INPUT_FNAME, 'r') as f:
        type_1_f, type_2_f, type_3_f = [open(fname, 'w') for fname in OUTPUT_FNAMES]

        for i, line in enumerate(f):
            print i, '\b'*10,
            if ((time.time() - t) / 60.) > 30:
                quit()
            tokens = re.split(TOKENIZATION_REGEX, line.lower())  # Might as well do proper tokenization here
            line_id = tokens[0]
            tokens = tokens[1:]
            idless_line = line[len(line_id):]
            
            # Type 1
            raw_hash = hashlib.md5(idless_line).digest()
            try:
                type_1_f.write(output(type_1s[raw_hash], line_id))
                continue
            except KeyError:
                type_1s[raw_hash] = line_id

            # Type 2
            non_stopwords = [token for token in tokens if token not in STOPWORDS]
            token_freqs = counter(non_stopwords)
            hashed_tokens = [
                [
                    (-1 if x == '0' else 1) * token_freqs[token]
                    for x in
                    bin(int(hashlib.md5(token).hexdigest(), 16))[2:].zfill(128)[:K]
                ]
                for token in 
                non_stopwords
            ]
            hashes = map(tuple, chunks(K / L, [0 if x < 1 else 1 for x in itertools.imap(sum, itertools.izip(*hashed_tokens))]))
            matching_docs = (
                doc
                for dict_, hash_ in
                itertools.izip(type_2s, hashes)
                for doc in
                dict_[hash_]
            )
            token_set = frozenset(token_freqs)
            try:
                next(
                    type_2_f.write(output(doc_id, line_id))
                    for doc_id, doc_tokens in
                    set(matching_docs)
                    if num_differences(token_set, doc_tokens) < 3
                )
                continue
            except StopIteration:
                pass
            exhaust(
                dict_[hash_].append((line_id, token_set))
                for dict_, hash_ in
                itertools.izip(type_2s, hashes)
            )

    exhaust(file_.close() for file_ in (type_1_f, type_2_f, type_3_f))


if __name__ == '__main__':
    import time
    t = time.time()
    main(t)
    print (time.time() - t) / 60.

