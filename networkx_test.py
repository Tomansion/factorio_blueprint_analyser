import networkx as nx
from pyvis.network import Network

net = Network()

# Create directed graph object
Graph = nx.DiGraph()

# Create nodes
Graph.add_node("C++")
Graph.add_node("Python")
Graph.add_node("Java")
Graph.add_node("C#")
Graph.add_node("Go")
Graph.add_node("Julia")

# For adding the edges between nodes with weight and value (Edges with higher value will appear as bold)
Graph.add_edge("C++", "C#", weight=.75, value=20)
Graph.add_edge("Python", "Julia", weight=.75, value=20)
Graph.add_edge("Java", "Go", weight=.5)
Graph.add_edge("Python", "C#", weight=.5)
Graph.add_edge("Go", "C++", weight=.5)
Graph.add_edge("Java", "Julia", weight=.5)
Graph.add_edge("Java", "C#", weight=.75, value=20)

# For visualizing the graph
net.from_nx(Graph)
net.show("graph.html")
