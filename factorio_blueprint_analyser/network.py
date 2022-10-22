from factorio_blueprint_analyser import node as node_service, utils
from pyvis.network import Network as NetworkDisplay

# -----------------------------------------------------------
# Create a node network from a blueprint
# Provide calculations methods
# -----------------------------------------------------------


def create_network(blueprint):
    network_creator = NetworkCreator(blueprint)
    network = network_creator.create_network()

    # We give the network to the blueprint
    # it will be used to export the analysis
    blueprint.network = network
    return network


class NetworkCreator:
    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.node_map = []

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
        node = node_service.create_node(entity)

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
                target_x = node.entity.position[0] + offset[0]
                target_y = node.entity.position[1] + offset[1]

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
                        possible_coord[0], possible_coord[1])

                    if child_node is not None and \
                            child_node.entity.name == node.entity.name and \
                            child_node.entity.belt_type == "output":

                        node.childs.append(child_node)
                        child_node.parents.append(node)
                        break

                    # No output belt found, print warning?

            return node

        elif node.type in ["container", "logistic-container"]:
            # Those entities does not interact with others
            self.node_map[y][x] = node
            return node

        elif node.type == "splitter":

            # We need to add the second splitter tile to the map
            if x == entity.position[0] and y == entity.position[1]:
                # If we are the original splitter, we need to add the second splitter
                self.node_map[y][x] = node

                second_belt_offset = entity.get_second_belt_offset()
                second_node_x = x + second_belt_offset[0]
                second_node_y = y + second_belt_offset[1]

                if second_node_x >= 0 and second_node_x < self.blueprint.width and\
                        second_node_y >= 0 and second_node_y < self.blueprint.heigth:
                    self.node_map[second_node_y][second_node_x] = node
            else:
                # We create the original splitter instead
                return self.create_node(entity.position[0], entity.position[1])

            # Set the entity where items are droped as the node's child
            drop_tile_offsets = entity.get_drop_tile_offsets()
            for offset in drop_tile_offsets:
                target_drop_x = x + offset[0]
                target_drop_y = y + offset[1]

                drop_child_node = self.create_node(
                    target_drop_x, target_drop_y)

                if drop_child_node is not None and entity.can_move_to(drop_child_node.entity):
                    node.childs.append(drop_child_node)
                    drop_child_node.parents.append(node)

            return node

        utils.warning(f"Unsupported entity type: {entity.data['type']}")
        return None


class Network:
    def __init__(self, blueprint, nodes_array):
        self.blueprint = blueprint
        self.nodes_array = nodes_array

        self.nodes = []

        for row in self.nodes_array:
            for node in row:
                if node is not None and not node.removed:
                    # Check that the node is not already in the list
                    # It's normal if the node takes multiple tiles
                    # (They appear multiple times in the map)
                    if node not in self.nodes:
                        self.nodes.append(node)

        self.optimize()

    def optimize(self):
        # We save the nodes original parents and childs
        for node in self.nodes:
            node.original_parents = [
                parent.entity.number for parent in node.parents]
            node.original_childs = [
                child.entity.number for child in node.childs]

        # Network optimisation
        for node in self.nodes:
            node.optimize()

        # Filter the removed nodes
        optimized_nodes = []

        for node in self.nodes:
            if not node.removed:
                optimized_nodes.append(node)

        self.nodes = optimized_nodes

    def get_node(self, entity_number) -> node_service.Node:
        for node in self.nodes:
            if node.entity.number == entity_number:
                return node

        return None

    def root_nodes(self):
        roots = []
        for node in self.nodes:
            if len(node.parents) == 0:
                roots.append(node)
        return roots

    def leaf_nodes(self):
        leafs = []
        for node in self.nodes:
            if len(node.childs) == 0:
                leafs.append(node)
        return leafs

    def calculate_bottleneck(self):
        # ==========================================
        # ====== Step 1: Purpose estimation ========
        # ==========================================

        # The first step is to calculate the purpose of each node
        # We will start from each assembling machine and go up and down
        # each parent and child node to tell them what we expect them to do

        # The purpose calculation starts from the assembly machines
        # childs as only one item is produced per assembling machine

        for node in self.nodes:
            if node.type == "assembling-machine":
                node.calculate_childs_purpose()

        # We will then, for the parents, deal with the assembling machines
        # with recipes that have one ingredient first as they are easier to process

        # Recipes with one ingredient first
        for node in self.nodes:
            if node.type == "assembling-machine" and\
                node.entity.recipe is not None and\
                    len(node.entity.recipe.ingredients) == 1:
                node.calculate_parents_purpose()

        # Recipes with multiple ingredients
        for node in self.nodes:
            if node.type == "assembling-machine" and\
                node.entity.recipe is not None and\
                    len(node.entity.recipe.ingredients) > 1:
                node.calculate_parents_purpose()

        # Display some debug info
        nb_transport_nodes_with_no_purpose = 0
        nb_transport_nodes = 0

        for node in self.nodes:
            if node.node_type == "transport_node":
                nb_transport_nodes += 1
                if node.transported_items is None or\
                        len(node.transported_items) == 0:
                    nb_transport_nodes_with_no_purpose += 1

        utils.verbose("")
        utils.success("Entities calculation estimation complete:")
        utils.verbose(
            f"{nb_transport_nodes - nb_transport_nodes_with_no_purpose} / {nb_transport_nodes} nodes with purpose")

        # ==============================================
        # ====== Step 2: Bottleneck calculation ========
        # ==============================================

        # We will try to estimate the use rate of all nodes
        # We start with the leaf nodes that have a purpose and
        # we will ask for the maximum produced item per second

        for node in self.leaf_nodes():
            items_output = node.get_materials_output()

            if items_output is None or len(items_output) == 0:
                continue

            # We ask each item that the node gives
            # If there is some capacity left with the item n,
            # we will ask for the item n+1 at the remaining capacity

            flow_capacity = node.entity.speed if node.entity.speed is not None else 10000

            for item_output in items_output:
                # We pass the flow to the node, it will send it to his childs
                acepted_amount = node.ask_flow(item_output.name, flow_capacity)
                flow_capacity -= acepted_amount

        utils.verbose("")
        utils.success("Bottleneck calculation complete!")
        utils.verbose("Produced items:")
        for node in self.leaf_nodes():
            # TODO: fix that nothing is shown for the bp blueprints4/drillFac1
            # None of the leaf nodes have a flow and none of them are processed by
            # the bottleneck algorithm (no node with 0 childs processed).
            # due to bp optimization ?
            for item in node.flow.items:
                utils.verbose(f"   {item}: {node.flow.items[item]} /s")

    def display(self):
        # Display the network as a node graph using the
        # networkx library
        net = NetworkDisplay(directed=True, height=1000, width=1900)
        net.repulsion(node_distance=80, spring_length=0)

        # Nodes and edges
        for node in self.nodes:
            # Define node size
            node_size = 3
            if node.type == "transport-belt":
                node_size = 3
            if node.type == "underground-belt" or "splitter":
                node_size = 4
            if node.type == "container" or "logistic-container":
                node_size = 3
            if node.type == "assembling-machine":
                node_size = 5
            if node.type == "inserter":
                node_size = 4

            # Display the node total items / second and the node use percentage
            node_label = ""
            bottleneck = False
            if node.node_type == "transport_node":
                node_label = str(
                    int(node.flow.total_amount * 100) / 100) + "/s "

                if node.usage_ratio is not None:
                    # Belts, arms, ...
                    node_label += str(int(node.usage_ratio * 100)) + "%"
                    bottleneck = int(node.usage_ratio * 100) >= 100

            net.add_node(node.entity.number,
                         value=node_size,
                         label=node_label,
                         shape="circularImage",
                         borderWidth=10,
                         color="lightgrey" if not bottleneck else "black",
                         image=node.entity.get_ingame_image_path(),
                         brokenImage="https://wiki.factorio.com/images/Warning-icon.png")

        for node in self.nodes:
            for child in node.childs:
                net.add_edge(node.entity.number,
                             child.entity.number,
                             value=1,
                             color="lightgrey")

        # Display recipes
        for node in self.nodes:
            if node.type == "assembling-machine" and node.entity.recipe is not None:
                node_id = str(node.entity.number) + "_recipe"

                # Display the produced items per sec
                items_per_sec = int(node.flow.total_amount * 100) / 100

                # Display the usage rate
                usage_rate = (str(int(node.usage_ratio * 100)) +
                              "%") if node.usage_ratio is not None else ""

                net.add_node(node_id,
                             label=str(items_per_sec) + "/s " + usage_rate,
                             value=3,
                             shape="image",
                             image=node.entity.recipe.get_ingame_image_path(),
                             brokenImage="https://wiki.factorio.com/images/Warning-icon.png")

                net.add_edge(node_id,
                             node.entity.number,
                             title="produce",
                             color="grey",
                             dashes=True,
                             arrowStrikethrough=False)

        # Display inputs
        for node in self.root_nodes():
            # TODO: Display the expected input materials
            node_id = str(node.entity.number) + "_root"
            net.add_node(node_id,
                         label="Input",
                         value=3,
                         shape="text")

            net.add_edge(node_id,
                         node.entity.number,
                         color="red",
                         dashes=True,
                         arrowStrikethrough=False)

        # Display outputs
        for node in self.leaf_nodes():
            # TODO: Display the expected produced materials
            node_id = str(node.entity.number) + "_leaf"
            net.add_node(node_id,
                         label="Output",
                         value=3,
                         shape="text")

            net.add_edge(node.entity.number,
                         node_id,
                         color="blue",
                         size=2,
                         dashes=True,
                         arrowStrikethrough=False)

        # Display nodes transported items and flow
        for node in self.nodes:
            if node.node_type == "transport_node" and node.transported_items is not None:
                for (i, item) in enumerate(node.transported_items):
                    node_id = str(node.entity.number) + "_item_" + str(i)

                    node_label = " "
                    if len(node.transported_items) > 1:
                        # We display the flow if there is one
                        if item.name in node.flow.items:
                            node_label = str(
                                int(node.flow.items[item.name] * 100) / 100) + "/s"

                    net.add_node(node_id,
                                 label=node_label,
                                 value=2,
                                 shape="image",
                                 image=item.get_ingame_image_path(),
                                 brokenImage="https://wiki.factorio.com/images/Warning-icon.png")

                    net.add_edge(node_id,
                                 node.entity.number,
                                 title="transport",
                                 color="lightgrey")

        # Display the graph
        net.show(self.blueprint.label.replace('/', '-') + ".html")
