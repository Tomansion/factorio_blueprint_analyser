from src import utils
from pyvis.network import Network as NetworkDisplay

# -----------------------------------------------------------
# Create a node network from a blueprint
# Provide calculations methods
# -----------------------------------------------------------


# ========= Network =========
def create_network(blueprint):
    network_creator = NetworkCreator(blueprint)
    return network_creator.create_network()


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
        node = Assembly_node(entity) \
            if entity.data["type"] == "assembling-machine" \
            else Transport_node(entity)

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
            if x == entity.position["x"] and y == entity.position["y"]:
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
                return self.create_node(entity.position["x"], entity.position["y"])

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

        utils.verbose(f"Unsupported entity type: {entity.data['type']}")
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
        # Network optimisation
        for node in self.nodes:
            node.optimize()

        # Filter the removed nodes
        optimized_nodes = []

        for node in self.nodes:
            if not node.removed:
                optimized_nodes.append(node)

        self.nodes = optimized_nodes

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
        # ===========================================
        # === Step 1: Purpose back propagation ======
        # ===========================================

        # The first step is to calculate the purpose of each node
        # We will start from each assembling machine and go up and down
        # each parent and child node to tell them what we expect them to do

        # The purpose calculation starts from the assembly machines
        # We will process the assembling machines with recipes that
        # have one ingredient first as they are easier to process

        for node in self.nodes:
            if node.type == "assembling-machine" and\
                    node.entity.recipe is not None and\
                    len(node.entity.recipe.ingredients) == 1:
                node.calculate_purpose()

        for node in self.nodes:
            if node.type == "assembling-machine" and\
                    node.entity.recipe is not None and\
                    len(node.entity.recipe.ingredients) > 1:
                node.calculate_purpose()

        # Display some debug info
        nb_transport_nodes_with_no_purpose = 0
        nb_transport_nodes = 0

        for node in self.nodes:
            if type(node) == Transport_node:
                nb_transport_nodes += 1
                if node.transported_items is None or\
                        len(node.transported_items) == 0:
                    nb_transport_nodes_with_no_purpose += 1

        utils.verbose("\nBottleneck analysis complete:")
        utils.verbose(
            f"{nb_transport_nodes - nb_transport_nodes_with_no_purpose} / {nb_transport_nodes} nodes with purpose")

    def display(self):
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

            net.add_node(node.entity.number,
                         value=node_size,
                         shape="circularImage",
                         borderWidth=10,
                         color="lightgrey",

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
                net.add_node(node_id,
                             label=node.entity.recipe.name,
                             value=3,
                             shape="image",
                             image=node.entity.recipe.get_ingame_image_path(),
                             brokenImage="https://wiki.factorio.com/images/Warning-icon.png")

                net.add_edge(node.entity.number,
                             node_id,
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

        # Display nodes transported items
        for node in self.nodes:
            if node.type != "assembling-machine" and node.transported_items is not None:
                for (i, item) in enumerate(node.transported_items):
                    node_id = str(node.entity.number) + "_item_" + str(i)
                    net.add_node(node_id,
                                 label=" ",
                                 value=2,
                                 shape="image",
                                 image=item.get_ingame_image_path(),
                                 brokenImage="https://wiki.factorio.com/images/Warning-icon.png")

                    net.add_edge(node_id,
                                 node.entity.number,
                                 title="transport",
                                 color="lightgrey")

        # Display the graph
        net.show("graph.html")

# ========= Nodes =========


class Node:
    def __init__(self, entity):
        # Network construction data
        self.entity = entity
        self.childs = []
        self.parents = []
        self.type = entity.data["type"]

        # Network optimization data
        self.removed = False
        self.compacted_nodes = []  # Contain the nodes deleted by the optimizer

    def optimize(self):
        # Optimize the graph by removing the node if it's not needed.

        if self.type == "transport-belt":
            # If the transport belt as a single belt parent with same name
            # and no childs, we can remove it
            if len(self.childs) == 0 and \
                    len(self.parents) == 1 and \
                    self.parents[0].entity.name == self.entity.name:
                #     and \
                # not self.parents[0].removed:

                self.remove()

            # If the transport belt as a single child
            # and a single belt parent with same name, we can remove it
            elif len(self.childs) == 1 and \
                    len(self.parents) == 1 and \
                    self.parents[0].entity.name == self.entity.name:
                #     and\
                # not self.parents[0].removed:

                self.remove()

    def remove(self):
        # Remove the node from the network
        if len(self.childs) > 1 or len(self.parents) != 1:
            raise Exception("Can't remove this node " + str(self))

        self.removed = True

        # We need to replace our parent child with our child
        self.parents[0].childs.remove(self)
        if len(self.childs) > 0:
            # We need to replace our child parent with our parent
            self.childs[0].parents.remove(self)
            if self.childs[0] != self.parents[0]:
                # This condition avoid belts loop to be removed
                self.childs[0].parents.append(self.parents[0])
                self.parents[0].childs.append(self.childs[0])

        # We keep a trace of this node by adding it to the compacted list
        self.compacted_nodes.append(self)
        self.parents[0].compacted_nodes += self.compacted_nodes

    def get_materials_output(self):
        # Get the materials output of the node
        # If the node is an assembling machine, the output is the recipe result
        # Else, the output is the node inputs
        return None

    def calculate_purpose(self):
        return None

    def set_purpose(self, items, from_node=None):
        return None

    def __str__(self):
        compatced_info = ""
        if len(self.compacted_nodes) > 0:
            compatced_info = "[⧈ " + str(len(self.compacted_nodes)) + "]"

        return f"{self.entity} [{len(self.parents)} ► {len(self.childs)}] {compatced_info}"


class Assembly_node (Node):
    def __init__(self, entity):
        super().__init__(entity)

        # Bottleneck calculation data
        self.inputs = []
        self.outputs = []

        if self.entity.recipe is not None:
            # Set the self inputs as the recipe ingredients
            for input_item in self.entity.recipe.ingredients:
                self.inputs.append(input_item)

            # Set the self outputs as the recipe result
            # We only consider that the recipes makes one item at the moment
            # TODO: Add support for multiple items
            self.outputs = [self.entity.recipe.result]

    def calculate_purpose(self):
        # Set our childrens and parents purpose

        if self.entity.recipe is None:
            return  # No purpose

        # We first set the purpose of our childs according to the outputs of the recipe
        for child in self.childs:
            child.set_purpose([self.entity.recipe.result], from_node=self)

        # We will assign our parents a purpose according to the recipe inputs and the
        # purpose our parents already have

        # If we have no parents, we are an inpot so we do nothing
        if len(self.parents) == 0:
            return

        if len(self.entity.recipe.ingredients) == 1:
            # We only need one ingredient to make the recipe
            # so our parents purpose is to provide the ingredient

            for parent in self.parents:
                # TODO: detect wrongly wired parents
                # The parent is wrong if it has a strict purpose and it's not the same as the recipe input
                parent.set_purpose(
                    self.entity.recipe.ingredients, from_node=self)

        else:
            # We need more than one ingredient to make the recipe,
            # but we don't know witch parent will provide which ingredient

            # === 1. Finding our parents purpose ===

            utils.verbose(
                f"Finding providers for recipe {self.entity.recipe.name} with ingredinents:")

            # So we start by getting all our parents output items
            parent_outputs = []
            for parent in self.parents:
                parent_output = parent.get_materials_output()
                parent_outputs.append(parent_output)

            # === 2. Finding if our ingredients are all available ===
            # for each of our ingredients, we try to find a parent
            # that provides the ingredient
            provided_ingredients = [None] * \
                len(self.entity.recipe.ingredients)

            for (ing_index, ingredient) in enumerate(self.entity.recipe.ingredients):
                utils.verbose(f"\t{ingredient}")
                provided_ingredients[ing_index] = []
                for (parent_ind, parent_output) in enumerate(parent_outputs):
                    for parent_item in parent_output:
                        if ingredient.name == parent_item.name:
                            # We found a parent that provides the ingredient
                            # We can ignore it and the ingredient it provides
                            provided_ingredients[ing_index].append(
                                parent_item)
                            utils.verbose(
                                f"\t\t{self.parents[parent_ind]} provides {ingredient}")

            nb_treated_ingredients = 0
            needed_ingredients = []
            for (i, provided_ingredient) in enumerate(provided_ingredients):
                if len(provided_ingredient) > 0:
                    nb_treated_ingredients += 1
                else:
                    needed_ingredients.append(
                        self.entity.recipe.ingredients[i])

            utils.verbose(
                f"\t  {nb_treated_ingredients}/{len(self.entity.recipe.ingredients)} provided ingredients")

            if nb_treated_ingredients == len(self.entity.recipe.ingredients):
                # We consider that all our ingredients are provided
                return

            # === 3. Assigning available parents to the missing ingredients ===

            # The parents with no purpose will provide the other ingredients
            parent_without_purpose = []
            for parent in self.parents:
                if parent.transported_items is None:
                    parent_without_purpose.append(parent)
                    utils.verbose(
                        f"\t\t{parent} has no purpose, it will provide the other ingredients")

            if len(parent_without_purpose) == 0:
                # No parent can provide the other ingredients
                # TODO Force on non strict transporters
                utils.verbose(
                    "WARNING: No parent can provide the other ingredients for the recipe " + self.entity.recipe.name)
                return

            # Assign the other ingredients to the parents
            for parent in parent_without_purpose:
                parent.set_purpose(needed_ingredients, from_node=self)

    def get_materials_output(self):
        # Get the materials output of the node
        # For a assembling machine node, the output is the recipe result

        return self.outputs

    def __str__(self):
        inputs = ""
        for item in self.inputs:
            inputs += str(item) + " "

        outputs = ""
        for item in self.outputs:
            outputs += str(item) + " "

        return f"Assembly node, {super().__str__()} [⭨ {inputs} ⭧ {outputs}]"


class Transport_node (Node):
    def __init__(self, entity):
        super().__init__(entity)

        # Bottleneck calculation data
        self.transported_items = None

    def get_materials_output(self):
        # Get the materials output of the node

        if self.transported_items is None:
            # We don't know what the node outputs are
            # so we ask our parents for their output
            transported_items = []
            for parent in self.parents:
                transported_items += parent.get_materials_output()

            if len(transported_items) > 0:
                self.transported_items = transported_items

            # items_output = ""
            # for item in transported_items:
            #     items_output += str(item) + " "
            # utils.verbose(f"                  {self} outputs: {items_output}")
            return transported_items

        # items_output = ""
        # for item in self.transported_items:
        #     items_output += str(item) + " "
        # utils.verbose(f"                  {self} outputs: {items_output}")

        return self.transported_items

    def set_purpose(self, items, from_node=None):
        if self.transported_items is not None:
            for item in items:
                for transported_item in self.transported_items:
                    if transported_item.name == item.name:
                        # We already transport the item so we can ignore it
                        break
        else:
            self.transported_items = items

            for parent in self.parents:
                if parent is not from_node:
                    parent.set_purpose(items, from_node=self)

            for child in self.childs:
                if child is not from_node:
                    child.set_purpose(items, from_node=self)

    def __str__(self):
        transported_items = ""

        if self.transported_items is None:
            transported_items = "?"

        elif len(self.transported_items) == 0:
            transported_items = "None"
        else:
            for item in self.transported_items:
                transported_items += str(item) + " "

        return f"Node {super().__str__()} [↔ {transported_items}]"
