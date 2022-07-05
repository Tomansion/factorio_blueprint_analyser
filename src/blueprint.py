import json
import sys

from src import utils, entity, options

# -----------------------------------------------------------
# Read the blueprint from the given file in the options
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

    def __init__(self, label, entities):
        self.label = label

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
            utils.verbose(f"No entities in the blueprint {label}")
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

                            utils.verbose(f"Adding temporary entity {container}")
                            self.array[drop_coord[1]
                                       ][drop_coord[0]] = container

    def is_coord_in_boundaries(self, coord):
        return coord[0] >= 0 and coord[0] < self.width and\
            coord[1] >= 0 and coord[1] < self.heigth

    def display(self):
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


def load_blueprint(file):
    # Read the file
    if file.endswith(".json"):
        # No need to decode the json
        with open(file, 'r') as f:
            bp_json = json.load(f)

    else:

        with open(file, 'r') as f:
            bp_encoded = f.read()
        bp_json = utils.decode(bp_encoded)

    # Check if the json is valid
    if "blueprint" not in bp_json:
        print("Invalid blueprint, no 'blueprint' key found")
        sys.exit(1)

    if "entities" not in bp_json["blueprint"]:
        print("Invalid blueprint, no 'blueprint' key found")
        sys.exit(1)

    blueprint_label = "No label"
    if "label" in bp_json["blueprint"]:
        blueprint_label = bp_json["blueprint"]["label"]

    utils.verbose(f"Blueprint {blueprint_label} loaded successfully")

    # Return the blueprint
    return Blueprint(blueprint_label, bp_json["blueprint"]["entities"])
