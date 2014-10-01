"""
Implement a simple word overlap retrieval algorithm (see lecture 3, slide 6). 
Your implementation (overlap.py) should read the query file (qrys.txt) and the
document file (docs.txt) from the current directory. Tokenize on punctuation
and lowercase the tokens, but don't do anything else to improve performance.
For each query Q and for each document D compute the overlap score between Q
and D. Output all scores into a file called overlap.top in the current
directory.
"""

import re
import functools
import collections


OUTPUT_FNAME = "overlap.top"


class BagOfWords(collections.namedtuple("BagOfWords", "id_ words")):
    def __new__(cls, tokenized_line):
        return super(BagOfWords, cls).__new__(
            cls,
            tokenized_line[0],
            set(tokenized_line[1:])
        )


def main():
    with open('qrys.txt') as f:
        queries = f.readlines()
    with open('docs.txt') as f:
        documents = f.readlines()

    tokenizer = functools.partial(re.findall, "[A-Za-z0-9]+")
    queries, documents = [
        [BagOfWords(tokenizer(line.lower())) for line in lines]
        for lines in 
        (queries, documents)
    ]

    output_lines = [
        ' 0 '.join(map(str, (
            query.id_,
            document.id_,
            len(query.words.intersection(document.words))
        )))
        for query in queries
        for document in documents
    ]

    with open(OUTPUT_FNAME, 'w') as f:
        f.write('\n'.join(line + ' 0 ' for line in output_lines))


if __name__ == "__main__":
    main()