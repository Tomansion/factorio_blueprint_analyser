import json

from factorio_blueprint_analyser import utils, entity, config

# -----------------------------------------------------------
# Read the blueprint from the given file
# Decode the file is encoded
# Create an entity list from the blueprint items
# Place the entities in a 2D array according to their position
# -----------------------------------------------------------


class Blueprint:
    entities = []
    label = ""
    heigth = 0
    width = 0
    array = []
    blueprint = None

    def __init__(self, bp_json):
        self.blueprint = bp_json

        # Check if the json is valid
        if "blueprint" not in bp_json:
            raise Exception("Invalid blueprint, no 'blueprint' key found")

        if "entities" not in bp_json["blueprint"]:
            # raise Exception("Invalid blueprint, no 'entities' key found")
            bp_json["blueprint"]["entities"] = []

        self.label = "No label"
        if "label" in bp_json["blueprint"]:
            self.label = bp_json["blueprint"]["label"]

        entities = bp_json["blueprint"]["entities"]

        # === Blueprint pre process ===

        # entities creation
        for entity_dic in entities:

            # Replace infinit chests with a normal chest
            if entity_dic["name"] == "infinity-chest":
                entity_dic["name"] = "iron-chest"

            # Creation of the entity from the blueprint entity dictionary
            new_entity = entity.create_entity(entity_dic)

            if new_entity is not None:
                self.entities.append(new_entity)

        if len(self.entities) == 0:
            utils.warning(f"No entities in the blueprint {self.label}")
            return

        # For some reason, the blueprint does not always start at 0,0 so we set a new origin:
        lowest_x = min(e.position[0] for e in self.entities)
        lowest_y = min(e.position[1] for e in self.entities)

        for entity_obj in self.entities:
            entity_obj.position[0] -= lowest_x
            entity_obj.position[1] -= lowest_y

        self.width = max(e.position[0] for e in self.entities) + 1
        self.heigth = max(e.position[1] for e in self.entities) + 1

        # === Convertion of the blueprint into a 2D array ===
        self.array = []

        for _ in range(self.heigth):
            self.array.append([None] * self.width)

        for created_entity in self.entities:
            if created_entity.large:
                # Because entites like the assembling machine is a 3x3 block,
                # we need to store it in the array 9 times
                for offset in created_entity.offsets:
                    offset_coord_x = offset[0] + created_entity.position[0]
                    offset_coord_y = offset[1] + created_entity.position[1]

                    # check that the offset is in the bondaries
                    if offset_coord_x >= self.width or offset_coord_x < 0:
                        continue

                    if offset_coord_y >= self.heigth or offset_coord_y < 0:
                        continue

                    self.array[offset_coord_y][offset_coord_x] = created_entity

            else:
                self.array[created_entity.position[1]
                           ][created_entity.position[0]] = created_entity

        # === Post process ===

        # Adding a temporary entity to the array where arms pickup or drop items
        # on an empty tile

        for y in range(self.heigth):
            for x in range(self.width):
                e = self.array[y][x]
                if e is not None and e.data["type"] == "inserter":
                    # Check drop tile
                    # If the drop tile is empty, add a virtual chest
                    # No need to check the pickup tile because the inserter
                    # will pickup the item from the virtual chest
                    # created by the other arm
                    drop_coord = e.get_drop_tile_coord()
                    if self.is_coord_in_boundaries(drop_coord):
                        drop_tile = self.array[drop_coord[1]][drop_coord[0]]
                        if drop_tile is None:
                            # The drop tile is empty, we add a temporary entity
                            container = entity.create_entity(
                                {
                                    'entity_number': str(e.number) + "_virtual\n(empty tile)",
                                    'name': 'wooden-chest',
                                    'position': {'x': drop_coord[0], 'y': drop_coord[1]}
                                }, virtual=True)

                            utils.verbose(
                                f"Adding temporary entity {container}")
                            self.array[drop_coord[1]
                                       ][drop_coord[0]] = container

        utils.success(f"Blueprint {self.label} loaded successfully")

    def is_coord_in_boundaries(self, coord):
        return coord[0] >= 0 and coord[0] < self.width and\
            coord[1] >= 0 and coord[1] < self.heigth

    def display(self):
        if config.config.verbose_level < 3:
            return

        utils.verbose(
            f"\n{self.label}, width: {self.width}, heigth: {self.heigth}, {len(self.entities)} entities:")
        for entity in self.entities:
            utils.verbose("  " + str(entity))

        utils.verbose("")
        for (y, row) in enumerate(self.array):
            utils.verbose("   ", end=" ")
            for (x, entity) in enumerate(row):
                if entity is None:
                    utils.verbose(" ", end=" ")
                else:
                    if entity.large:
                        utils.verbose(entity.to_char([x, y]), end=" ")
                    else:
                        utils.verbose(entity.to_char(), end=" ")
            utils.verbose("")
        utils.verbose("")

    def get_analysis(self):
        # Read the blueprint network if it exists
        # Then fill the information in a new dictionary

        if self.network is None:
            raise Exception("No network found")

        # Base blueprint format :
        # "blueprint": {
        #     "icons": [...],
        #     "entities": [
        #         {
        #             "entity_number": 1,
        #             "name": "transport-belt",
        #             "position": {...},
        #             "direction": 2
        #         },
        #         {
        #             "entity_number": 2,
        #             "name": "assembly-machine-1",
        #             "position": {...},
        #             "direction": 2
        #         },
        #         {
        #             "entity_number": 3,
        #             "name": "transport-belt",
        #             "position": {...}
        #         }
        #     ],
        #     "item": "blueprint",
        #     "label": "beltFac1",
        #     "version": 281479275544576
        # }

        # Analysed blueprint format:
        # "blueprint": {
        #     "icons": [...],
        #     "entities": [
        #         {
        #             "entity_number": 1,
        #             "name": "transport-belt",
        #             "position": {...},
        #             "direction": 2,
        #
        #             "input": True,
        #             "transpoted_items": [{"iron-plate": 1.26}],
        #             "usage_rate": 0.87,
        #             "parents": [2],
        #             "childrens": [3, 4]
        #         },
        #         {
        #             "entity_number": 2,
        #             "name": "assembly-machine-1",
        #             "position": {...},
        #             "recipe": "transport-belt"
        #
        #             "usage_rate": 0.84,
        #             "parents": [...],
        #             "childrens": [...]
        #         },
        #         {
        #             "entity_number": 3,
        #             "name": "transport-belt",
        #             "position": {...},
        #
        #             "output": True
        #             "transpoted_items": [{"transport-belt": 0.84}],
        #             "usage_rate": 0.52,
        #             "parents": [...],
        #             "childrens": [...]
        #         }
        #     ],
        #     "item": "blueprint",
        #     "label": "beltFac1",
        #     "version": 281479275544576,
        #
        #     "items_input": [{"iron-plate": 1.26}],
        #     "items_output": [{"transport-belt": 0.84}],
        #     "entities_input": [1, 2, 3, ...],
        #     "entities_output": [32, 33, 34, ...],
        #     "entities_bottleneck": [18, 23],
        # }

        analysed_bp = self.blueprint.copy()

        # Pre load network input and output
        root_entities_number = [
            node.entity.number for node in self.network.root_nodes()]
        leaf_entities_number = [
            node.entity.number for node in self.network.leaf_nodes()]

        entities_bottleneck = []

        # Entities related information
        for entity in analysed_bp["blueprint"]["entities"]:
            node = self.network.get_node(entity["entity_number"])

            if node is None:
                continue

            # Adding usage_rate
            usage_rate = node.usage_ratio
            if usage_rate is not None:
                entity["usage_rate"] = usage_rate

                # If the node as been "compacted" with other entities
                # due to optimization, we need to update the oser entites
                for compacted_node in node.compacted_nodes:
                    compacted_entity = self._get_entity(
                        compacted_node.entity.number, analysed_bp["blueprint"]["entities"])
                    compacted_entity["usage_rate"] = usage_rate

                    # Adding bottleneck entities number
                    if usage_rate >= 1:
                        entities_bottleneck.append(
                            compacted_entity["entity_number"])

                # Adding bottleneck entities number
                if usage_rate >= 1:
                    entities_bottleneck.append(entity["entity_number"])

            # Adding input/output
            if node.entity.number in root_entities_number:
                entity["input"] = True

                for compacted_node in node.compacted_nodes:
                    compacted_entity = self._get_entity(
                        compacted_node.entity.number, analysed_bp["blueprint"]["entities"])
                    compacted_entity["input"] = True

            if node.entity.number in leaf_entities_number:
                entity["output"] = True

                for compacted_node in node.compacted_nodes:
                    compacted_entity = self._get_entity(
                        compacted_node.entity.number, analysed_bp["blueprint"]["entities"])
                    compacted_entity["output"] = True

            # Adding transpoted_items
            entity["transpoted_items"] = node.flow.items
            for compacted_node in node.compacted_nodes:
                compacted_entity = self._get_entity(
                    compacted_node.entity.number, analysed_bp["blueprint"]["entities"])
                compacted_entity["transpoted_items"] = node.flow.items

            # Adding parents and childrens
            entity["parents"] = node.original_parents
            entity["children"] = node.original_childs

            for compacted_node in node.compacted_nodes:
                compacted_entity = self._get_entity(
                    compacted_node.entity.number, analysed_bp["blueprint"]["entities"])

                compacted_entity["parents"] = compacted_node.original_parents
                compacted_entity["children"] = compacted_node.original_childs

        # Blueprint related information
        # Adding the total in and out flow
        items_input = []
        for root_node in self.network.root_nodes():
            items_input.append(root_node.flow.items)

        items_output = []
        for leaf_node in self.network.leaf_nodes():
            items_output.append(leaf_node.flow.items)

        analysed_bp["items_input"] = items_input
        analysed_bp["items_output"] = items_output

        # Adding the entities input and output
        analysed_bp["entities_input"] = root_entities_number
        analysed_bp["entities_output"] = leaf_entities_number

        # Adding the entities bottleneck
        analysed_bp["entities_bottleneck"] = entities_bottleneck

        return analysed_bp

    def _get_entity(self, entity_number, entites):
        for entity in entites:
            if entity["entity_number"] == entity_number:
                return entity

        return {}


def load_blueprint(blueprint_sting):
    try:
        # Try to read the string directly as a JSON
        blueprint_json = json.loads(blueprint_sting)
    except json.decoder.JSONDecodeError:
        # If it fails, try to decode it
        blueprint_json = utils.decode(blueprint_sting)

    return Blueprint(blueprint_json)


def load_blueprint_from_path(file_path):
    # Read the file
    if file_path.endswith(".json"):
        # No need to decode the json
        with open(file_path, 'r') as f:
            bp_json = json.load(f)

    else:
        with open(file_path, 'r') as f:
            bp_encoded = f.read()
        bp_json = utils.decode(bp_encoded)

    return Blueprint(bp_json)
