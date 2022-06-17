
import ujson

from src import utils

# -----------------------------------------------------------
# Provide for the other files Factorio data
# from the src/assets/factorio_raw/factorio_raw_min.json file
# -----------------------------------------------------------

factorio_raw_data_file_path = "src/assets/factorio_raw/factorio_raw_min.json"
# TODO: read from options instead


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

    # TODO:. check that the file exists
    with open(factorio_raw_data_file_path, "r") as f:
        data = ujson.load(f)

        # Load the recipies
        if recipies_key not in data:
            print(f"WARNING: no {recipies_key} key found in Factorio data")

        recipies = data[recipies_key]

        # Load the items
        if items_key not in data:
            print(f"WARNING: no {items_key} key found in Factorio data")

        items = data[items_key]

        # Load the entities
        for key in entities_categories_keys:
            if key not in data:
                print(
                    f"WARNING: no {key} entity category found if Factorio data")
            else:
                for entity in data[key]:
                    entities[entity] = data[key][entity]

        # ==== process the entities ====
        # Find the entity size size fron the selection_box data
        #    Expected results:
        #    [1,1] for the belts and arms,
        #    [3,3] for the assembling machines

        # for entity in entities:
        #     if "selection_box" not in entities[entity]:
        #         print(f"WARNING: no selection_box found in {entity} entity")
        #         entity["size"] = [1, 1]
        #         continue

        utils.verbose(f"Factorio data loaded")


def entity_exist(entity):
    # TODO
    pass
