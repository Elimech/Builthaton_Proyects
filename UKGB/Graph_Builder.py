import networkx as nx

def build_graph(triples):
    G = nx.DiGraph()

    for subj, rel, obj in triples:
        G.add_node(subj)
        G.add_node(obj)
        G.add_edge(subj, obj, label=rel)

    return G
