
# -----------------------------------------------------------
# Create a node network from a blueprint
# Provide calculations methods for the network
# -----------------------------------------------------------

from platform import node

from responses import target


def create_network(blueprint):
    network_creator = NetworkCreator(blueprint)
    return network_creator.create_network()


class NetworkCreator:

    blueprint = {}
    node_map = []

    def __init__(self, blueprint):
        self.blueprint = blueprint

    def create_network(self):
        # Create a 2D array that will contain all nodes,
        # the same way as the blueprint array
        # The nodes will then be exctarcted from the 2D array in a list
        # Knowing where the nodes are located from each other will be useful

        self.node_map = []

        for _ in range(self.blueprint.heigth):
            self.node_map += [[None for _ in range(self.blueprint.width)]]

        # Iterate over the blueprint entities
        for i in range(self.blueprint.heigth):
            for j in range(self.blueprint.width):
                self.create_node(i, j)

        network = Network(self.blueprint)
        # network.create_nodes()
        # network.create_edges()
        return network

    def create_node(self, i, j):
        # Returns a node object or None
        print("creating node at", i, j)

        # Check if the cell hasn't been filled yet
        if self.node_map[i][j] is not None:
            return self.node_map[i][j]

        # Get the entity at the current position
        entity = self.blueprint.array[i][j]

        if entity is None:
            return None

        node = Node(entity)

        if node.type == "transport-belt":
            # Set the entity in front as the node's child
            tile_in_front_offset = entity.get_tile_in_front_offset()

            target_x = i + tile_in_front_offset[0]
            target_y = j + tile_in_front_offset[1]

            if not (target_x < 0 or target_x >= self.blueprint.heigth or
                    target_y < 0 or target_y >= self.blueprint.width):
                node_child = self.create_node(target_x, target_y)

                if node_child is not None:
                    print("child node found at", target_x, target_y)
                    node.childs.append(node_child)

        # if entity.data["type"] == "assembling-machine":


class Network:
    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.nodes = []
        self.edges = []

    def create_nodes(self):
        for entity in self.blueprint.entities:
            self.nodes.append(Node(entity))

    def create_edges(self):
        for node in self.nodes:
            for neighbour in node.neighbours:
                self.edges.append(Edge(node, neighbour))

    def display(self):
        for node in self.nodes:
            print(node)
        for edge in self.edges:
            print(edge)


class Node:
    def __init__(self, entity):
        self.entity = entity
        self.childs = []
        self.type = entity.data["type"]
        # self.position = entity.position
        # self.name = entity.data["name"]
        # print(entity)
        # self.direction = entity.data["direction"]
        # self.offsets = entity.offsets
        # self.connections = entity.connections
        # self.connections_count = len(self.connections)
        # self.connections_count_str = str(self.connections_count)
        # self.connections_count_str_len = len(self.connections_count_str)

    def __str__(self):
        return f"Node: {self.entity.data['name']}"


# class Edge:
#     def __init__(self, node1, node2):
#         self.node1 = node1
#         self.node2 = node2
#         # self.type = "edge"
#         # self.weight = 1
#         # self.direction = "none"
#         # self.distance = 0
#         # self.distance_str = ""
#         # self.distance_str_len = 0

#     def __str__(self):
#         return f"{self.node1.name} -> {self.node2.name}"
