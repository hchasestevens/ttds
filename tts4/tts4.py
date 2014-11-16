from collections import defaultdict
import itertools
import operator
import copy
import math
import re


def counter(items):
    """Psuedo-reimplementation of collections.Counter"""
    d = defaultdict(int)
    for item in items:
        d[item] += 1
    return d


def main():
    messages = defaultdict(lambda: defaultdict(set))
    connections = defaultdict(lambda: defaultdict(int))
    pointing_to_node = defaultdict(set)
    num_out_connections = defaultdict(float)
    emails = set()
    message_emails = defaultdict(set)
    edges = defaultdict(int)
    with open('graph.txt') as f:
        split_lines = (line.lower().split() for line in f)
        message_groups = itertools.groupby(split_lines, operator.itemgetter(1))
        for from_email, message_group in message_groups:
            from_email_messages = messages[from_email]
            from_email_connections = connections[from_email]
            for message_id, __, to_email in message_group:
                if to_email == from_email: continue
                emails.add(from_email)
                emails.add(to_email)
                message_emails[message_id].add(from_email)
                message_emails[message_id].add(to_email)
                from_email_messages[to_email].add(message_id)
                num_out_connections[from_email] += 1  # nice sum for from_email
                from_email_connections[to_email] += 1
                pointing_to_node[to_email].add(from_email)

    message_subjects = {}
    messages_mentioning = defaultdict(set)
    token_counts = defaultdict(float)
    with open('subject.txt') as f:
        for message_id, message_subject in (line.split('  ', 1) for line in f):
            subject_tokens = filter(bool, re.split('\W+', message_subject.lower()))
            message_subjects[message_id] = subject_tokens
            for token in set(subject_tokens):
                token_counts[token] += 1
                messages_mentioning[token].add(message_id)
    num_messages = len(message_subjects)
    idf = dict((token, math.log(num_messages/count)) for token, count in token_counts.iteritems())
    stopwords = frozenset(sorted(idf.iterkeys(), key=idf.get)[:50])

    num_nodes = float(len(emails))

    initial_pagerank = 1. / num_nodes 
    lambda_ = 0.8
    page_ranks = dict((email, initial_pagerank) for email in emails)
    sink_nodes = frozenset(email for email in emails if not connections[email])
    
    initial_hub_authority_score = 1. / math.sqrt(num_nodes)
    hubs = dict((email, initial_hub_authority_score) for email in emails)
    authorities = copy.copy(hubs)

    for i in xrange(20):
        print i + 1

        if i < 10:
            # Update pagerank
            old_page_ranks = copy.copy(page_ranks)
            sink_node_mass = sum(old_page_ranks[sink_node] for sink_node in sink_nodes)
            page_ranks = dict(
                (node_to_update, lambda_ * sum(
                    connections[node][node_to_update] * old_page_ranks[node] / num_out_connections[node]
                    for node in 
                    pointing_to_node[node_to_update]
                ) + (1 - lambda_ + lambda_ * sink_node_mass) / num_nodes)
                for node_to_update in
                emails
            )

        # Update H&A
        old_hubs = copy.copy(hubs)
        old_authorities = copy.copy(authorities)
        hubs = dict(
            (node_to_update, sum(
                old_authorities[node] * weight
                for node, weight in
                connections[node_to_update].iteritems()
            ))
            for node_to_update in 
            emails
        )
        authorities = dict(
            (node_to_update, sum(
                old_hubs[node] * connections[node][node_to_update]
                for node in
                pointing_to_node[node_to_update]
            ))
            for node_to_update in
            emails
        )

        # Normalize:
        hub_sum_squares = math.sqrt(sum(value ** 2 for value in hubs.itervalues()))
        authority_sum_squares = math.sqrt(sum(value ** 2 for value in authorities.itervalues()))
        hubs = dict((k, v / hub_sum_squares) for k, v in hubs.iteritems())
        authorities = dict((k, v / authority_sum_squares) for k, v in authorities.iteritems())
    
    assert abs(hubs['jeff.dasovich@enron.com'] - 0.001006) < 0.00001
    assert abs(authorities['jeff.dasovich@enron.com'] - 0.000210) < 0.00001
    assert abs(page_ranks['jeff.dasovich@enron.com'] - 0.0020586) < 0.000001
    assert abs(page_ranks['john.lavorato@enron.com'] - 0.0015712) < 0.000001

    best_hubs = sorted(((v, k) for k, v in hubs.iteritems()), reverse=True)[:100]
    best_authorities = sorted(((v, k) for k, v in authorities.iteritems()), reverse=True)[:100]
    best_pageranks = sorted(((v, k) for k, v in page_ranks.iteritems()), reverse=True)[:100]

    with open('hubs.txt', 'w') as f:
        f.write('\n'.join('{0:.6f} {1}'.format(*hub) for hub in best_hubs))
    with open('auth.txt', 'w') as f:
        f.write('\n'.join('{0:.6f} {1}'.format(*auth) for auth in best_authorities))
    with open('pr.txt', 'w') as f:
        f.write('\n'.join('{0:.6f} {1}'.format(*pr) for pr in best_pageranks))

    best_hubs = [email for __, email in best_hubs]
    best_authorities = [email for __, email in best_authorities]
    best_pageranks = [email for __, email in best_pageranks]
    best_best_pageranks = frozenset(best_pageranks[:7])
    meta_wordcloud = defaultdict(int)
    for a, b in itertools.product(best_best_pageranks, best_best_pageranks):
        word_cloud = counter(word 
            for message_id in filter(bool, messages[a][b])
            for word in message_subjects[message_id]
            if word not in stopwords
        )
        if word_cloud:
            for word, count in word_cloud.iteritems():
                meta_wordcloud[word] += count
    most_important_words = sorted(meta_wordcloud, key=meta_wordcloud.get, reverse=True)[:10]
    print most_important_words

    interesting_email_counts = counter(
        email
        for word in most_important_words
        for m in messages_mentioning[word]
        for email in message_emails[m]
    )
    interesting_email_counts = dict(
        (email, 
         float(count) 
         * max(d[email] for d in (page_ranks, )) 
         #/ ((num_out_connections[email] + from_email_connections[email]) or float('inf'))
        )
        for email, count
        in interesting_email_counts.iteritems()
    )
    print sorted(interesting_email_counts, key=interesting_email_counts.get, reverse=True)[:10]
    print sorted(interesting_email_counts, key=interesting_email_counts.get, reverse=True)[10:20]



if __name__ == "__main__":
    main()