import math
from src import utils, item

# -----------------------------------------------------------
# Network nodes properties
# -----------------------------------------------------------


def create_node(entity):
    return Assembly_node(entity) \
        if entity.data["type"] == "assembling-machine" \
        else Transport_node(entity)


class Node:
    def __init__(self, entity):
        # Network construction data
        self.entity = entity
        self.childs = []
        self.parents = []
        self.type = entity.data["type"]
        # self.direct_input = False
        # Network optimization data
        self.removed = False
        self.compacted_nodes = []  # Contain the nodes deleted by the optimizer

        # Bottleneck calculation
        self.flow = item.Flow()

    # Optimization
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

    # Purpose estimation
    def get_materials_output(self):
        # Get the materials output of the node
        # If the node is an assembling machine, the output is the recipe result
        # Else, the output is the node inputs
        return None

    def calculate_purpose(self):
        return None

    def set_purpose(self, items, from_node=None):
        return None

    def connected_to_input(self):
        # True if no assembly mach between the node and the root
        if self.node_type == "assembling-machine":
            return False

        if len(self.parents) == 0:
            return True

        for parent in self.parents:
            if parent.connected_to_input():
                return True

        return False

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # If the node is an assembling machine, the input is the recipe inputs
        # Else, the input is the node outputs
        return None

    # Other
    def __str__(self):
        compacted_info = ""
        if len(self.compacted_nodes) > 0:
            compacted_info = "[⧈ " + str(len(self.compacted_nodes)) + "]"

        return f"{self.entity} [{len(self.parents)} ► {len(self.childs)}] {compacted_info}"


class Assembly_node (Node):
    def __init__(self, entity):
        super().__init__(entity)
        self.node_type = "assembly_node"

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

        self.ingredients_input = {}
        self.usage_ratio = None

    def __str__(self):
        inputs = ""
        for item in self.inputs:
            inputs += str(item) + " "

        outputs = ""
        for item in self.outputs:
            outputs += str(item) + " "

        return f"Assembly node, {super().__str__()} [⭨ {inputs} ⭧ {outputs}]"

    # Purpose estimation
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

            if len(parent_without_purpose) > 0:
                # Assign the other ingredients to the parents
                for parent in parent_without_purpose:
                    parent.set_purpose(needed_ingredients, from_node=self)
                return

            # === 4. Assigning root connected parents to the missing ingredients ===

            # No available parents can provide the other ingredients
            # So we will find the parents that are directly connected to an input
            # without passing through another assembly node

            for parent in self.parents:
                if parent.connected_to_input():
                    utils.verbose(
                        f"\t\t{parent} has is an input, it will provide the other ingredients")

                    parent.set_purpose(needed_ingredients, from_node=self)
                    return

            # No parent can provide the other ingredients
            print(
                f"Waring No parent can provide the other ingredients for {self}")

    def get_materials_output(self):
        # Get the materials output of the node
        # For a assembling machine node, the output is the recipe result

        return self.outputs

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # For a assembling machine node, the input is the recipe inputs

        if self.entity.recipe is None:
            return None

        return self.inputs

    def give_flow(self, item, amount):
        # We receive a flow from a parent
        if self.entity.recipe is None:
            # If no recipe, we accept no flow
            return 0

        if len(self.parents) == 0:
            # If no parents, we are an input,
            # so we supose that we have all the elements we need

            for ingredient in self.entity.recipe.ingredients:
                self.ingredients_input[ingredient.name] = math.inf

            # we just send our childrens our produced item
            self.send_childs_recipe_results()
            return amount

        # We check that the given item is in our recipe
        if not self.entity.recipe.ingredient_required(item):
            return 0

        # We store the flow in our inputs
        if item not in self.ingredients_input:
            self.ingredients_input[item] = amount
        else:
            self.ingredients_input[item] += amount

        # We check if we have enough ingredients to make the recipe
        if self.entity.recipe.all_ingredients_required(self.ingredients_input.keys()):
            self.send_childs_recipe_results()

        # We tell our parent how much we take from the flow
        required_ingredient_nb = self.entity.recipe.get_ingredient_nb(item)

        required_ingredient_nb_per_second = required_ingredient_nb / self.entity.time_per_item

        if required_ingredient_nb_per_second >= amount:
            # We have the capacity to take all the
            return amount

        # Current limitaitons:
        # We are still accepting our parent flow, but we should not
        # if our childrens can't accept our flow for some reason
        # TODO: show this with a test

        # # Fix that only work if we have one parent:
        # if len(self.parents) == 1:
        #     # We can't take all the flow, we take the rest
        #     return item.Flow(flow.items, required_ingredient_nb_per_second * self.usage_ratio)

        return required_ingredient_nb_per_second

    def send_childs_recipe_results(self):
        # We send our recipe results to our childs
        # At the moment, we split the recipe result
        # for each child

        usage_ratio = self.entity.get_usage_ratio(self.ingredients_input)
        produced_items_per_second = self.entity.items_per_second * usage_ratio

        recipe_result = self.entity.recipe.result.name
        amount_to_send = produced_items_per_second

        # If we have already sended items, we need to send the difference
        if self.flow.total_amount >= produced_items_per_second:
            # We don't have more flow than we can send
            return 0

        amount_to_send = produced_items_per_second - self.flow.total_amount

        sended_amount = 0
        for child in self.childs:
            accepted_amount = child.give_flow(recipe_result, amount_to_send)
            sended_amount += accepted_amount
            amount_to_send -= accepted_amount

        self.flow.add_item(self.entity.recipe.result, sended_amount)
        self.usage_ratio = self.flow.total_amount / self.entity.items_per_second


class Transport_node (Node):
    def __init__(self, entity):
        super().__init__(entity)
        self.node_type = "transport_node"

        # Bottleneck calculation data
        self.transported_items = None

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

    # Purpose estimation
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
                item_already_in_list = False
                for transported_item in self.transported_items:
                    if transported_item.name == item.name:
                        # We already transport the item so we can ignore it
                        item_already_in_list = True
                        break

                if not item_already_in_list:
                    self.transported_items.append(item)

        else:
            self.transported_items = items

            for parent in self.parents:
                if parent is not from_node:
                    parent.set_purpose(items, from_node=self)

            for child in self.childs:
                if child is not from_node:
                    child.set_purpose(items, from_node=self)

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # For a transport node, the input is the transported items
        return self.transported_items

    @property
    def capacity(self):
        if self.entity.speed is None:
            return None

        return self.flow.total_amount / self.entity.speed

    def give_flow(self, item, amount):
        # An item flow is given to the node
        processed_amount = amount

        if self.entity.speed is None:
            # Node without speed or capacity limits (chests)
            self.flow.add_item(item, amount)
            return self.send_childs_flow(item, amount)

        if self.capacity >= 1:
            # We are full, we can't accept the flow
            return 0

        # We get only the flow we can accept
        available_flow_amount = self.entity.speed - self.flow.total_amount

        if available_flow_amount < processed_amount:
            # We have an exceding flow,
            # we can't accept all of the second flow
            processed_amount = available_flow_amount

        # How much of this new flow can our children accept
        accepted_amount = self.send_childs_flow(item, processed_amount)

        # We add it to our flow
        self.flow.add_item(item, accepted_amount)

        return accepted_amount

    def send_childs_flow(self, item, amount):
        # If we don't have children, we are an output node
        if len(self.childs) == 0:
            # so we accept all the input flow
            return amount

        # If we have one child, we try to give it the flow
        elif len(self.childs) == 1:
            return self.childs[0].give_flow(item, amount)

        # If we have multiple children,
        # We give the flow to each childs, they are sorted by priority
        # TODO: sort by priority (arms with higer speed first, ...)
        # If there is some flow left from a previous child, we give it to the next child

        leftover_amount = amount
        sended_amount = 0
        for child in self.childs:
            accepted_amount = child.give_flow(item, leftover_amount)
            sended_amount += accepted_amount
            leftover_amount -= accepted_amount

        return sended_amount
