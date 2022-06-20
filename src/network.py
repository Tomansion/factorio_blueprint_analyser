from src import utils

# -----------------------------------------------------------
# Create a node network from a blueprint
# Provide calculations methods
# -----------------------------------------------------------


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
        # Knowing where the nodes are located from each other will be useful

        # The nodes will then be exctracted from the 2D array in a list

        self.node_map = []

        for _ in range(self.blueprint.heigth):
            self.node_map += [[None for _ in range(self.blueprint.width)]]

        # Iterate over the blueprint entities
        # to create each nodes recursively
        for y in range(self.blueprint.heigth):
            for x in range(self.blueprint.width):
                self.create_node(x, y)

        # Optimize the network
        # TODO: Remove belts that follow each others

        return Network(self.blueprint, self.node_map)

    def create_node(self, x, y):
        # Returns a node object or None

        # Check if the cell hasn't been filled yet
        if x < 0 or x >= self.blueprint.width or y < 0 or y >= self.blueprint.heigth:
            return None

        # Check if a node already exists in the cell
        if self.node_map[y][x] is not None:
            return self.node_map[y][x]

        # Get the entity at the given position
        entity = self.blueprint.array[y][x]

        if entity is None:
            return None

        # We can now create the node
        node = Node(entity)

        # Each game entity interacts with the other nodes in there own way
        # The requiered nodes will be created recursively
        if node.type == "transport-belt":
            # The node is inserted in the map to avoid infinit recursion
            self.node_map[y][x] = node

            # We want to set the entity in front of the belt as the node's child
            # We get the coordinates of the entity in front of the belt:
            tile_in_front_offset = entity.get_tile_in_front_offset()
            target_x = x + tile_in_front_offset[0]
            target_y = y + tile_in_front_offset[1]

            # We get the node in front of the belt or create a new one
            child_node = self.create_node(target_x, target_y)

            if child_node is not None and entity.can_connect_to(child_node.entity):
                node.childs.append(child_node)
                child_node.parents.append(node)

            return node

        elif node.type == "inserter":
            # The node is inserted in the map to avoid infinit recursion
            self.node_map[y][x] = node

            # Set the entity where items are droped as the node's child
            tile_drop_offset = entity.get_drop_tile_offset()
            target_drop_x = x + tile_drop_offset[0]
            target_drop_y = y + tile_drop_offset[1]

            drop_child_node = self.create_node(target_drop_x, target_drop_y)

            if drop_child_node is not None and entity.can_move_to(drop_child_node.entity):
                node.childs.append(drop_child_node)
                drop_child_node.parents.append(node)

            # Set the entity where items are picked up as the node's parent
            tile_pickup_offset = entity.get_pickup_tile_offset()
            target_pickup_x = x + tile_pickup_offset[0]
            target_pickup_y = y + tile_pickup_offset[1]

            pickup_node = self.create_node(target_pickup_x, target_pickup_y)

            if pickup_node is not None and entity.can_move_from(pickup_node.entity):
                node.parents.append(pickup_node)
                pickup_node.childs.append(node)

            return node

        elif node.type == "assembling-machine":
            # We will create 9 nodes for the 9 tiles of the assembling machine
            # All the cells are the same object, they share their parents and childs
            for offset in node.entity.offsets:
                target_x = node.entity.position["x"] + offset[0]
                target_y = node.entity.position["y"] + offset[1]

                if target_x < 0 or target_x >= self.blueprint.width\
                        or target_y < 0 or target_y >= self.blueprint.heigth:
                    continue

                self.node_map[target_y][target_x] = node
            return node

        elif node.type == "underground-belt":
            self.node_map[y][x] = node

            if entity.belt_type == "output":
                # Set the entity where items are droped as the node's child
                # Exactly the same as for the transport belt
                tile_in_front_offset = entity.get_tile_in_front_offset()
                target_x = x + tile_in_front_offset[0]
                target_y = y + tile_in_front_offset[1]

                # We get the node in front of the belt or create a new one
                child_node = self.create_node(target_x, target_y)

                if child_node is not None and entity.can_connect_to(child_node.entity):
                    node.childs.append(child_node)
                    child_node.parents.append(node)
            else:
                # We try to connect to the output belt
                possible_output_coords = entity.get_possible_output_coords()
                for possible_coord in possible_output_coords:
                    child_node = self.create_node(
                        possible_coord["x"], possible_coord["y"])

                    if child_node is not None and \
                            child_node.type == "underground-belt" and \
                            child_node.entity.belt_type == "output":

                        node.childs.append(child_node)
                        child_node.parents.append(node)
                        break

                    # No output belt found, print warning?

            return node

        elif node.type == "container":
            # Those entities does not interact with others
            self.node_map[y][x] = node
            return node

        utils.verbose(f"Unsupported entity type: {entity.data['type']}")
        return None


class Network:
    def __init__(self, blueprint, nodes_array):
        self.blueprint = blueprint
        self.nodes_array = nodes_array

        self.nodes = []

        for row in self.nodes_array:
            for node in row:
                if node is not None:
                    # Check that the node is not already in the list
                    # It can happen if the node takes multiple tiles
                    if node not in self.nodes:
                        self.nodes.append(node)

    def get_root_nodes(self):
        roots = []
        for node in self.nodes:
            if len(node.parents) == 0:
                roots.append(node)
        return roots

    def get_leef_nodes(self):
        leafs = []
        for node in self.nodes:
            if len(node.childs) == 0:
                leafs.append(node)
        return leafs

    def display(self):
        for node in self.nodes:
            print(node)

        print("\nRoot nodes:")
        for node in self.get_root_nodes():
            print(node)
        print("Leef nodes:")
        for node in self.get_leef_nodes():
            print(node)


class Node:
    def __init__(self, entity):
        self.entity = entity
        self.childs = []
        self.parents = []
        self.type = entity.data["type"]

    def __str__(self):
        return f"Node: {self.entity}, childs: {len(self.childs)}, parents: {len(self.parents)}"


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