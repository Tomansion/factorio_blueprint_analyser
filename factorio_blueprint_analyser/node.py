from factorio_blueprint_analyser import utils, item

# -----------------------------------------------------------
# Network nodes properties
# -----------------------------------------------------------


def create_node(entity):
    if entity.data["type"] == "assembling-machine":
        return Assembly_node(entity)
    else:
        return Transport_node(entity)


class Node:
    def __init__(self, entity):
        # Network construction data
        self.entity = entity
        self.childs = []
        self.parents = []
        self.original_parents = []
        self.original_childs = []
        self.type = entity.data["type"]

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

                self.remove()

            # If the transport belt as a single child
            # and a single belt parent with same name, we can remove it
            elif len(self.childs) == 1 and \
                    len(self.parents) == 1 and \
                    self.parents[0].entity.name == self.entity.name:

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

    def set_purpose_from_parent(self, items):
        pass

    def set_purpose_from_child(self, items):
        pass

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

        # Purpose calculation data
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

    def __str__(self):
        inputs = ""
        for item in self.inputs:
            inputs += str(item) + " "

        outputs = ""
        for item in self.outputs:
            outputs += str(item) + " "

        return f"Assembly node, {super().__str__()} [⭨ {inputs} ⭧ {outputs}]"

    # Purpose estimation
    def calculate_childs_purpose(self):
        # Set our childrens purpose

        if self.entity.recipe is None:
            return  # No purpose

        # We just set the purpose of our childs according to the outputs of the recipe
        for child in self.childs:
            child.set_purpose_from_parent([self.entity.recipe.result])

    def calculate_parents_purpose(self):
        # Set our parents purpose

        if self.entity.recipe is None:
            return  # No purpose

        # We will assign our parents a purpose according to the recipe inputs and the
        # purpose our parents already have

        # If we have no parents, we are an input, there is nothing more to do
        if len(self.parents) == 0:
            return

        if len(self.entity.recipe.ingredients) == 1:
            # We only need one ingredient to make the recipe
            # so our parents purpose is to provide the ingredient

            for parent in self.parents:
                # Creating a copy of the recipe input to avoid modifying the recipe
                recipe_ingredients = self.entity.recipe.ingredients[:]
                parent.set_purpose_from_child(recipe_ingredients)

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
                    parent.set_purpose_from_child(needed_ingredients)
                return

            # === 4. Assigning root connected parents to the missing ingredients ===

            # No available parents can provide the other ingredients
            # So we will find the parents that are directly connected to an input
            # without passing through another assembly node

            for parent in self.parents:
                if parent.connected_to_input():
                    utils.verbose(
                        f"\t\t{parent} is directly linked to an input, it will provide the other ingredients")

                    parent.set_purpose_from_child(needed_ingredients)
                    return

            # No parent can provide the other ingredients
            utils.verbose(
                f"Waring No parent can provide the other ingredients for {self}", level=1)

    def get_materials_output(self):
        # Get the materials output of the node
        # For a assembling machine node, the output is the recipe result

        return self.outputs

    # Bottleneck calculation
    @property
    def usage_ratio(self):
        if self.entity.recipe is None:
            return None

        return self.flow.total_amount / self.entity.items_per_second

    def get_materials_input(self):
        # Get the materials input of the node
        # For a assembling machine node, the input is the recipe inputs

        if self.entity.recipe is None:
            return None

        return self.inputs

    def ask_flow(self, item_name, amount):
        # We receive a flow request from a child

        if self.entity.recipe is None:
            # If no recipe, we give no flow
            return 0

        # We check that we produce the requested item
        if self.entity.recipe.result.name != item_name:
            return 0

        # We check that we have enougth assembly time
        available_amount = self.entity.items_per_second - self.flow.total_amount

        if available_amount <= 0:
            # We don't have enough assembly time to produce the requested amount
            return 0

        amount_that_need_to_be_produced = min(amount, available_amount)
        usage = amount_that_need_to_be_produced / self.entity.items_per_second

        if len(self.parents) == 0:
            # If no parents, we are an input,
            # so we supose that we have all the elements we need
            self.flow.add_item(item_name, amount_that_need_to_be_produced)
            return amount_that_need_to_be_produced

        # We check that we have the needed ingredients
        # so we ask for each of our items how much our parents can provide
        ingredients_input = {}
        for item in self.entity.recipe.ingredients:
            ingredients_input[item.name] = {"total": 0, "from": []}

            # We need to get the amount of the item we need the parents to provide
            # First we get the amount of the item that we would have needed in case of a 100% usage
            required_item_per_second = self.entity.required_items_per_second[item.name]

            # Then we reduce it to correspond to the amount of the item we expect to produce
            required_item_per_second *= usage
            required_item_per_second_target = required_item_per_second

            # We then ask our parents for the item:
            for parent in self.parents:
                amount_provided = parent.ask_flow(
                    item.name, required_item_per_second)
                ingredients_input[item.name]["from"].append({
                    "amount": amount_provided, "from": parent})
                ingredients_input[item.name]["total"] += amount_provided
                required_item_per_second -= amount_provided

                if required_item_per_second <= 0:
                    break

            if ingredients_input[item.name]["total"] == 0:
                # We don't have the needed ingredient, we can't proceed
                usage = 0
                break

            percent_recieved = ingredients_input[item.name]["total"] / \
                required_item_per_second_target

            # If the percent of the item we received is less than 100%,
            # we have to adjust our next items requests because
            # we don't need as much as expected

            usage *= percent_recieved

        produced_amount = usage * self.entity.items_per_second
        self.flow.add_item(self.entity.recipe.result.name, produced_amount)

        # Before sending how much item we can produce
        # we need to update our parents flow

        for ingredient_name in ingredients_input:
            required_item_per_second = self.entity.required_items_per_second[ingredient_name]
            real_required_amount = required_item_per_second * usage
            if ingredients_input[ingredient_name]["total"] > real_required_amount:
                # We asked too much, we need to give back
                exceeding_amount = ingredients_input[ingredient_name]["total"] - \
                    real_required_amount

                for amount_from in ingredients_input[ingredient_name]["from"]:
                    parent = amount_from["from"]
                    reduced_flow = parent.take_back_flow(
                        ingredient_name, exceeding_amount)
                    exceeding_amount -= reduced_flow

                    if exceeding_amount <= 0:
                        break

        return produced_amount

    def take_back_flow(self, item_name, amount):
        # We gived too much flow at some point, we take it back

        if self.entity.recipe is None:
            return 0

        # We check that we produce the requested item
        if self.entity.recipe.result.name != item_name:
            return 0

        if self.flow.total_amount <= 0:
            return 0

        # We get only take back the flow we can take back
        amount_to_take_back = amount
        if amount > self.flow.total_amount:
            amount_to_take_back = self.flow.total_amount

        percentage_to_take_back = amount_to_take_back / self.flow.total_amount

        # We ask our parents to take back their flow
        for item in self.entity.recipe.ingredients:
            actual_required_amount = self.usage_ratio * \
                self.entity.required_items_per_second[item.name]

            item_amount_to_take_back = actual_required_amount * percentage_to_take_back

            for parent in self.parents:
                amount_taked_back = parent.take_back_flow(
                    item.name, item_amount_to_take_back)
                item_amount_to_take_back -= amount_taked_back

                if item_amount_to_take_back <= 0:
                    break

        self.flow.reduce(item_name, amount_to_take_back)
        return amount_to_take_back


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

            return transported_items

        return self.transported_items

    def set_purpose_from_child(self, items):
        # Our childrens are telling us the items that they need
        self.add_transported_item(items)

        # We send the message to our parents
        for parent in self.parents:
            parent.set_purpose_from_child(items)

    def set_purpose_from_parent(self, items):
        # Our parents are telling us the items that they will give us
        self.add_transported_item(items)

        # We send the message to our childs
        for child in self.childs:
            child.set_purpose_from_parent(items)

    def add_transported_item(self, items):
        if self.transported_items is None:
            self.transported_items = items
        else:
            for item in items:
                item_already_in_list = False
                for transported_item in self.transported_items:
                    if transported_item.name == item.name:
                        # We already transport the item so we can ignore it
                        item_already_in_list = True
                        break

                if not item_already_in_list:
                    self.transported_items.append(item)

    def is_item_transported(self, item_name):
        if self.transported_items is None:
            return False

        for transported_item in self.transported_items:
            if transported_item.name == item_name:
                return True

        return False

    # Bottleneck calculation
    def get_materials_input(self):
        # Get the materials input of the node
        # For a transport node, the input is the transported items
        return self.transported_items

    @property
    def usage_ratio(self):
        if self.entity.speed is None:
            return None

        return self.flow.total_amount / self.entity.speed

    def ask_flow(self, item_name, amount):
        # An item flow is requiered from a parent node
        # We check that we tranport the requested item
        if not self.is_item_transported(item_name):
            return 0

        if self.entity.speed is None:
            # Node without speed or usage_ratio limits (chests)
            provided_amount = self.get_parents_flow(item_name, amount)
            self.flow.add_item(item_name, provided_amount)
            return provided_amount

        if self.usage_ratio >= 1:
            # We are full, we can't give more flow
            return 0

        # We get only the flow we can accept
        available_flow_amount = self.entity.speed - self.flow.total_amount

        processed_amount = amount
        if available_flow_amount < processed_amount:
            # We have an exceding flow,
            # we can't accept all of the second flow
            processed_amount = available_flow_amount

        # How much of this new flow can our children accept
        provided_amount = self.get_parents_flow(item_name, processed_amount)
        self.flow.add_item(item_name, provided_amount)
        return provided_amount

    def get_parents_flow(self, item_name, amount):
        # If we don't have parents, we are an input node
        if len(self.parents) == 0:
            # so we provide all the requested flow
            return amount

        # If we have one parent, we request from him the flow
        elif len(self.parents) == 1:
            return self.parents[0].ask_flow(item_name, amount)

        # If we have multiple parents,
        # We ask them each the flow, they are sorted by priority
        # TODO: sort by priority (arms and arms with higer speed first, ...)

        requested_amount = amount
        sendedable_amount = 0
        for parent in self.parents:
            provided_amount = parent.ask_flow(item_name, requested_amount)
            sendedable_amount += provided_amount
            # If there is some usage_ratio left afetr the previous parent,
            # we ask the next parent
            requested_amount -= provided_amount
            if requested_amount <= 0:
                break

        return sendedable_amount

    def take_back_flow(self, item_name, amount):
        # We gived too much flow at some point, we take it back
        if amount <= 0:
            return 0

        # We check that we tranport the requested item
        if not self.is_item_transported(item_name):
            return 0

        if self.entity.speed is None:
            # Node without speed or usage_ratio limits (chests)
            taked_back_amount = self.take_back_parents_flow(item_name, amount)
            self.flow.reduce(item_name, taked_back_amount)
            return taked_back_amount

        if self.usage_ratio <= 0:
            # We don't have flow to take back
            return 0

        # We get only take back the flow we can take back
        amount_to_take_back = amount
        if amount > self.flow.total_amount:
            amount_to_take_back = self.flow.total_amount

        # How much of this new flow can our children accept
        taked_back_amount = self.take_back_parents_flow(
            item_name, amount_to_take_back)
        self.flow.reduce(item_name, taked_back_amount)
        return taked_back_amount

    def take_back_parents_flow(self, item_name, amount):
        # Same as get_parents_flow but to take it back

        if len(self.parents) == 0:
            # Input node
            return amount

        elif len(self.parents) == 1:
            return self.parents[0].take_back_flow(item_name, amount)

        amount_to_take_back = amount
        taked_back_amount_total = 0
        for parent in self.parents:

            taked_back_amount = parent.take_back_flow(
                item_name, amount_to_take_back)
            taked_back_amount_total += taked_back_amount
            amount_to_take_back -= taked_back_amount
            if amount_to_take_back <= 0:
                break

        return taked_back_amount_total
