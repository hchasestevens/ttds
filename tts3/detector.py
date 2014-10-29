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
from _collections import defaultdict

INPUT_FNAME = "data.train"
OUTPUT_FNAMES = (
    "type{}.dup".format(n + 1)
    for n in 
    xrange(3)
)


def exhaust(gen):  # may want to replace with with list comp w/o assignment
    for item in gen:
        pass


def output(*args):
    return "{} {}\n".format(*sorted(args))


def main():
    type_1s = defaultdict(list)
    with open(INPUT_FNAME, 'r') as f:
        type_1_f, type_2_f, type_3_f = [open(fname, 'w') for fname in OUTPUT_FNAMES]

        for i, line in enumerate(f):
            print i, '\b'*10,
            tokens = line.lower().split()  # Might as well do proper tokenization here
            line_id = tokens[0]
            idless_line = line[len(line_id):]
            
            raw_hash = hashlib.md5(idless_line).digest()
            type_1_results = type_1s[raw_hash]
            exhaust(
                type_1_f.write(output(other_id, line_id))
                for other_id, other_line in
                type_1_results
                if other_line == idless_line
            )
            type_1_results.append((line_id, idless_line))

    exhaust(file_.close() for file_ in (type_1_f, type_2_f, type_3_f))


if __name__ == '__main__':
    main()

