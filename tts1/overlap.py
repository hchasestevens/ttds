"""
Implement a simple word overlap retrieval algorithm (see lecture 3, slide 6). 
Your implementation (overlap.py) should read the query file (qrys.txt) and the
document file (docs.txt) from the current directory. Tokenize on punctuation
and lowercase the tokens, but don't do anything else to improve performance.
For each query Q and for each document D compute the overlap score between Q
and D. Output all scores into a file called overlap.top in the current
directory.
"""