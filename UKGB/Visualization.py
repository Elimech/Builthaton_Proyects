from pyvis.network import Network
import os

def visualize_graph(G):
    net = Network(
        height="750px", 
        width="100%", 
        directed=True, 
        cdn_resources="in_line"
    )

    net.force_atlas_2based(
        gravity=-100,      
        central_gravity=0.01,
        spring_length=200,  
        spring_strength=0.05,
        damping=0.4
    )

    for node in G.nodes():
        connections = G.degree(node)
        color = "#fd7e14" if connections >= 3 else "#0d6efd"
        
        net.add_node(
            node, 
            label=node, 
            size=20 + (connections * 5), 
            color=color,
            shadow=True
        )

    for edge in G.edges(data=True):
        net.add_edge(
            edge[0], 
            edge[1], 
            label=edge[2].get("label", ""),
            color="#848484",
            smooth={'type': 'curvedCW', 'roundness': 0.15}
        )

    net.set_options("""
    var options = {
      "physics": {
        "stabilization": { "iterations": 200 }
      },
      "edges": {
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } },
        "font": { "size": 10, "align": "middle" }
      }
    }
    """)

    static_path = os.path.join(os.getcwd(), "static")
    net.save_graph(os.path.join(static_path, "graph.html"))