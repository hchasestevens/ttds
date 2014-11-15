from collections import defaultdict
import itertools
import operator
import copy


def main():
    messages = defaultdict(lambda: defaultdict(set))
    connections = defaultdict(lambda: defaultdict(int))
    pointing_to_node = defaultdict(set)
    num_out_connections = defaultdict(float)
    emails = set()
    with open('graph.txt') as f:
        split_lines = (line.split() for line in f)
        message_groups = itertools.groupby(split_lines, operator.itemgetter(1))
        for from_email, message_group in message_groups:
            emails.add(from_email)
            from_email_messages = messages[from_email]
            from_email_connections = connections[from_email]
            for message_id, __, to_email in message_group:
                if to_email == from_email: continue
                emails.add(to_email)
                from_email_messages[to_email].add(message_id)
                num_out_connections[from_email] += 1  # nice sum for from_email
                from_email_connections[to_email] += 1
                pointing_to_node[to_email].add(from_email)


    num_nodes = float(len(emails))
    initial_pagerank = 1. / num_nodes 
    lambda_ = 0.8
    page_ranks = {email: initial_pagerank for email in emails}
    sink_nodes = frozenset(email for email in emails if not connections[email])
    for i in xrange(10):
        print i + 1
        print page_ranks['jeff.dasovich@enron.com']
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
    assert abs(page_ranks['jeff.dasovich@enron.com'] - 0.002059) < 0.0001

    print sorted(page_ranks.iterkeys(), key=page_ranks.get, reverse=True)[:10]


if __name__ == "__main__":
    main()