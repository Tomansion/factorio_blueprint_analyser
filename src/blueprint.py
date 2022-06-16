import json
import sys
from importlib_metadata import NullFinder

from matplotlib.pyplot import cla
from src import utils

# -----------------------------------------------------------
# Read the blueprint from the given file in the options
# If the file is an encoded json, it will be decoded
# -----------------------------------------------------------


class Entity:
    def __init__(self, dictionary_entity):

        # Input example:
        # {
        #     'entity_number': 18,
        #     'name': 'inserter',
        #     'position': {'x': 10, 'y': -90},
        #     'direction': 6
        # }

        self.number = dictionary_entity["entity_number"]
        self.name = dictionary_entity["name"]
        self.original_position = dictionary_entity["position"]
        self.position = {
            "x": int(dictionary_entity["position"]["x"] + 0.5),
            "y": int(dictionary_entity["position"]["y"] + 0.5),
        }
        if "direction" in dictionary_entity:
            self.direction = dictionary_entity["direction"]
        else:
            self.direction = None

    def __str__(self):
        return f"{self.number} {self.name} [{self.position['x']}, {self.position['y']}] [{self.original_position['x']}, {self.original_position['y']}]"


class Blueprint:
    entities = []
    label = ""

    def __init__(self, label, entities):
        self.label = label

        for entity in entities:
            self.entities.append(Entity(entity))

    def display(self):
        utils.verbose(f"{len(self.entities)} entities")
        utils.verbose("")
        for entity in self.entities:
            utils.verbose("  " + str(entity))


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
