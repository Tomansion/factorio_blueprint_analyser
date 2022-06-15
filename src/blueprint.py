import json
import sys

from matplotlib.pyplot import cla
from src import utils

# -----------------------------------------------------------
# Read the blueprint from the given file in the options
# If the file is an encoded json, it will be decoded
# -----------------------------------------------------------


class Blueprint:
    entities = []
    label = ""

    def __init__(self, label, entities):
        self.label = label
        self.entities = entities


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
