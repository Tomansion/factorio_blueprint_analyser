import json
import sys

from src import utils, entity

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
            self.entities.append(entity.Entity(entity_dic))

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
            self.array.append([" "] * self.width)

        for entity in self.entities:
            self.array[entity.position["y"]
                       ][entity.position["x"]] = entity.to_char()

    def display(self):
        utils.verbose(
            f"\n{self.label}, width: {self.width}, heigth: {self.heigth}, {len(self.entities)} entities:")
        for entity in self.entities:
            utils.verbose("  " + str(entity))

    def display_array(self):
        for row in self.array:
            for cell in row:
                print(cell, end="")
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
