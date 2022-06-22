import json
import sys

from src import utils, entity, options

# -----------------------------------------------------------
# Read the blueprint from the given file in the options
# If the file is an encoded json, it will be decoded
# -----------------------------------------------------------


class Blueprint:
    entities = []
    label = ""
    heigth = 0
    width = 0
    array = []

    def __init__(self, label, entities):
        self.label = label

        for entity_dic in entities:

            # Replace infinit chests with a normal chest
            if entity_dic["name"] == "infinity-chest":
                entity_dic["name"] = "iron-chest"

            new_entity = entity.create_entity(entity_dic)
            if new_entity is not None:
                self.entities.append(new_entity)

        # Set the blueprint origin to [0, 0]
        lowest_x = min(entity.position["x"] for entity in self.entities)
        lowest_y = min(entity.position["y"] for entity in self.entities)

        for entity_obj in self.entities:
            entity_obj.position["x"] -= lowest_x
            entity_obj.position["y"] -= lowest_y

        self.width = max(entity.position["x"] for entity in self.entities) + 1
        self.heigth = max(entity.position["y"] for entity in self.entities) + 1

        self.store_in_array()
        self.display_array()

    def store_in_array(self):
        # store the entities list to a 2D array
        self.array = []

        for _ in range(self.heigth):
            self.array.append([None] * self.width)

        for entity in self.entities:
            if entity.large:
                # Because entites like the assembling machine is a 3x3 block,
                # we need to store it in the array 9 times
                for offset in entity.offsets:
                    offset_coord_x = offset[0] + entity.position["x"]
                    offset_coord_y = offset[1] + entity.position["y"]

                    # check that the offset is in the bondaries
                    if offset_coord_x >= self.width or offset_coord_x < 0:
                        continue

                    if offset_coord_y >= self.heigth or offset_coord_y < 0:
                        continue

                    self.array[offset_coord_y][offset_coord_x] = entity

            else:
                self.array[entity.position["y"]][entity.position["x"]] = entity

    def display(self):
        utils.verbose(
            f"\n{self.label}, width: {self.width}, heigth: {self.heigth}, {len(self.entities)} entities:")
        for entity in self.entities:
            utils.verbose("  " + str(entity))

    def display_array(self):
        if not options.silent:
            print("display")
            print("")
            for (y, row) in enumerate(self.array):
                print("   ", end=" ")
                for (x, entity) in enumerate(row):
                    if entity is None:
                        print(" ", end=" ")
                    else:
                        if entity.large:
                            print(entity.to_char([x, y]), end=" ")
                        else:
                            print(entity.to_char(), end=" ")
                print("")
            print("")


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
