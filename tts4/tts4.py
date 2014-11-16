from collections import defaultdict
import itertools
import operator
import copy
import math
import re


def main():
    messages = defaultdict(lambda: defaultdict(set))
    connections = defaultdict(lambda: defaultdict(int))
    pointing_to_node = defaultdict(set)
    num_out_connections = defaultdict(float)
    emails = set()
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
                from_email_messages[to_email].add(message_id)
                num_out_connections[from_email] += 1  # nice sum for from_email
                from_email_connections[to_email] += 1
                pointing_to_node[to_email].add(from_email)

    message_subjects = {}
    token_counts = defaultdict(float)
    with open('subject.txt') as f:
        for message_id, message_subject in (line.split('  ', 1) for line in f):
            subject_tokens = re.split('\W+', message_subject)
            message_subjects[message_id] = subject_tokens
            for token in subject_tokens:
                token_counts[token] += 1


    num_nodes = float(len(emails))

    initial_pagerank = 1. / num_nodes 
    lambda_ = 0.8
    page_ranks = {email: initial_pagerank for email in emails}
    sink_nodes = frozenset(email for email in emails if not connections[email])
    
    initial_hub_authority_score = 1. / math.sqrt(num_nodes)
    hubs = {email: initial_hub_authority_score for email in emails}
    authorities = copy.copy(hubs)

    for i in xrange(20):
        print i + 1

        if i < 10:
            # Update pagerank
            old_page_ranks = copy.copy(page_ranks)
            sink_node_mass = sum(old_page_ranks[sink_node] for sink_node in sink_nodes)
            page_ranks = {
                node_to_update: lambda_ * sum(
                    connections[node][node_to_update] * old_page_ranks[node] / num_out_connections[node]
                    for node in 
                    pointing_to_node[node_to_update]
                ) + (1 - lambda_ + lambda_ * sink_node_mass) / num_nodes
                for node_to_update in
                emails
            }

        # Update H&A
        old_hubs = copy.copy(hubs)
        old_authorities = copy.copy(authorities)
        hubs = {
            node_to_update: sum(
                old_authorities[node] * weight
                for node, weight in
                connections[node_to_update].iteritems()
            )
            for node_to_update in 
            emails
        }
        authorities = {
            node_to_update: sum(
                old_hubs[node] * connections[node][node_to_update]
                for node in
                pointing_to_node[node_to_update]
            )
            for node_to_update in
            emails
        }

        # Normalize:
        hub_sum_squares = math.sqrt(sum(value ** 2 for value in hubs.itervalues()))
        authority_sum_squares = math.sqrt(sum(value ** 2 for value in authorities.itervalues()))
        hubs = {k: v / hub_sum_squares for k, v in hubs.iteritems()}
        authorities = {k: v / authority_sum_squares for k, v in authorities.iteritems()}
    
    print
    print hubs['jeff.dasovich@enron.com']
    print authorities['jeff.dasovich@enron.com']
    print page_ranks['jeff.dasovich@enron.com']
    print
    assert abs(hubs['jeff.dasovich@enron.com'] - 0.001006) < 0.00001
    assert abs(authorities['jeff.dasovich@enron.com'] - 0.000210) < 0.00001
    assert abs(page_ranks['jeff.dasovich@enron.com'] - 0.0020586) < 0.000001
    assert abs(page_ranks['john.lavorato@enron.com'] - 0.0015712) < 0.000001

    best_hubs = frozenset(sorted(hubs.iterkeys(), key=hubs.get, reverse=True)[:10])
    best_authorities = frozenset(sorted(authorities.iterkeys(), key=authorities.get, reverse=True)[:10])
    best_pagerank = frozenset(sorted(page_ranks.iterkeys(), key=page_ranks.get, reverse=True)[:10])
    print best_hubs
    print best_authorities
    print best_pagerank
    print
    print best_authorities & best_pagerank
    #for a, b in itertools.product(best_authorities, best_authorities):
    #    for message_id in messages[a][b]:
    #        print a, b
    #        __ = raw_input(message_subjects[message_id])
    #    print



if __name__ == "__main__":
    main()