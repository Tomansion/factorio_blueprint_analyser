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

        # Network optimization data
        self.removed = False
        self.compacted_nodes = []  # Contain the nodes deleted by the optimizer

        # Bottleneck calculation
        self.flow = None

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

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # If the node is an assembling machine, the input is the recipe inputs
        # Else, the input is the node outputs
        return None

    # Other
    def __str__(self):
        compatced_info = ""
        if len(self.compacted_nodes) > 0:
            compatced_info = "[⧈ " + str(len(self.compacted_nodes)) + "]"

        return f"{self.entity} [{len(self.parents)} ► {len(self.childs)}] {compatced_info}"


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

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # For a assembling machine node, the input is the recipe inputs

        if self.entity.recipe is None:
            return None

        return self.inputs

    def give_flow(self, flow):
        # We receive a flow from a parent
        # at the moment, we accept all flows
        return flow

    # Other

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
        self.node_type = "transport_node"

        # Bottleneck calculation data
        self.transported_items = None
        self.flow = None

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

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # For a transport node, the input is the transported items
        return self.transported_items

    # def get_supported_item_amount(self):
    #     # TODO : priority
    #     pass

    @property
    def capacity(self):
        if self.flow is None:
            return None

        return self.flow.amount / self.entity.speed

    def give_flow(self, flow):
        # An item flow is given to the node
        # TODO: check transported items
        processed_flow = flow

        # If we have already a flow, we merge the two flows
        if self.flow is not None:
            if self.capacity >= 1:
                # We are full, we can't accept the flow
                return item.Flow([], 0)

            # We get only the flow we can accept
            available_flow_amount = self.entity.speed - self.flow.amount

            if available_flow_amount < processed_flow.amount:
                # We have an exceding flow,
                # we can't accept all of the second flow
                processed_flow = item.Flow(
                    self.flow.items, available_flow_amount)

            # How much of this new flow can our children accept
            processed_flow = self.send_childs_flow(processed_flow)

            # We add it to our flow
            self.flow = item.merge_flows([processed_flow, self.flow])

        else:
            # First time we receive a flow
            # We check if we can support the given flow
            if flow.amount > self.entity.speed:
                # We can't support it, we take the maximum we can support
                processed_flow = item.Flow(flow.items, self.entity.speed)

            # Then we ask our childrens
            processed_flow = self.send_childs_flow(processed_flow)

            # We save the flow
            self.flow = processed_flow

        return processed_flow

    def send_childs_flow(self, flow):
        # If we don't have children, we are an output node
        if len(self.childs) == 0:
            # so we accept all the input flow
            return flow

        # If we have one child, we try to give it the flow
        elif len(self.childs) == 1:
            return self.childs[0].give_flow(flow)

        # If we have multiple children,
        # We give the flow to each childs, they are sorted by priority
        # If there is some flow left from a previous child, we give it to the next child
        leftover_flow = flow
        cumulated_flow = 0
        for child in self.childs:
            child_flow = child.give_flow(leftover_flow)
            cumulated_flow += child_flow.amount
            leftover_flow = item.Flow(
                leftover_flow.items,
                leftover_flow.amount - child_flow.amount
            )

        return item.Flow(flow.items, cumulated_flow)
