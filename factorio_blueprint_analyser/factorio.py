
import json

from factorio_blueprint_analyser import utils, config

# -----------------------------------------------------------
# Provide for the other files Factorio data
# from the factorio_blueprint_analyser/assets/factorio_raw/factorio_raw_min.json file
# -----------------------------------------------------------

recipies_key = "recipe"
recipies = {}

items_key = "item"
items = {}

entities_categories_keys = [
    "splitter",
    "container",
    "logistic-container",
    "assembling-machine",
    "infinity-container",
    "inserter",
    "underground-belt",
    "furnace",
    "transport-belt",
]
entities = {}


def load_data():
    global recipies, entities, items
    factorio_raw_data_file_path = config.config.data_file_path

    # TODO:. check that the file exists
    with open(factorio_raw_data_file_path, "r") as f:
        data = json.load(f)

        # Load the recipies
        if recipies_key not in data:
            utils.warning(f"Recipe key {recipies_key} not found in Factorio data")

        recipies = data[recipies_key]

        # Load the items
        if items_key not in data:
            utils.warning(f"Item key {items_key} not found in Factorio data")

        items = data[items_key]

        # Load the entities
        for key in entities_categories_keys:
            if key not in data:
                utils.warning(
                    f"Entity {key} category not found if Factorio data")
            else:
                for entity in data[key]:
                    entities[entity] = data[key][entity]

        utils.success(f"Factorio data successfully loaded")


def entity_exist(entity):
    # TODO
    pass
