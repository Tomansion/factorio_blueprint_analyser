from math import floor
from termcolor import colored

from src import utils, factorio


def create_entity(entity_in_blueprint):
    # entity_in_blueprint examples:
    # {
    #     'entity_number': 18,
    #     'name': 'inserter',
    #     'position': {'x': 10, 'y': -90},
    #     'direction': 6
    # }
    # {
    #     "entity_number": 15,
    #     "name": "assembling-machine-1",
    #     "position": {
    #         "x": 3.5,
    #         "y": -90.5
    #     },
    #     "recipe": "iron-gear-wheel"
    # },

    # Check that the entity exists in the Factorio data
    if entity_in_blueprint["name"] not in factorio.entities:
        print(
            f"Warning: entity {entity_in_blueprint['name']} not found in Factorio data")
        # sys.exit(1)
        return None

    entity_data = factorio.entities[entity_in_blueprint["name"]]

    # Return the corresponding Entity object
    if entity_data["type"] == "transport-belt":
        return TransportBelt(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "assembling-machine":
        return AssemblingMachine(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "inserter":
        return Inserter(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "container":
        return Container(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "underground-belt":
        return UndergroundBelt(entity_in_blueprint, entity_data)

    print(f"Warning: entity {entity_in_blueprint['name']} not supported")


class Entity:
    def __init__(self, entity_in_blueprint, entity_data):
        self.data = entity_data
        self.number = entity_in_blueprint["entity_number"]
        self.name = entity_in_blueprint["name"]

        # Correc position
        self.original_position = entity_in_blueprint["position"]
        self.position = {
            "x": floor(entity_in_blueprint["position"]["x"]),
            "y": floor(entity_in_blueprint["position"]["y"]),
        }

        # Get the direction
        if "direction" in entity_in_blueprint:
            self.direction = entity_in_blueprint["direction"]
        else:
            self.direction = None

    def __str__(self):
        return f"{self.number} {self.name} [{self.position['x']}, {self.position['y']}] [{self.original_position['x']}, {self.original_position['y']}]" + " " + self.to_char()

    def to_char(self):
        return '?'


class TransportBelt (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

    def to_char(self):
        color = "white"
        if self.name == "transport-belt":
            color = "yellow"
        if self.name == "fast-transport-belt":
            color = "red"
        if self.name == "express-transport-belt":
            color = "blue"

        # ← ↑ → ↓
        if self.direction == 2:
            return colored("→", color)
        elif self.direction == 4:
            return colored("↓", color)
        elif self.direction == 6:
            return colored("←", color)
        else:
            return colored("↑", color)


class Inserter (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

    def to_char(self):
        color = "white"
        if self.name == "inserter":
            color = "yellow"
        if self.name == "long-handed-inserter":
            color = "red"
        if self.name == "fast-inserter":
            color = "blue"

        # ► ▼ ▲ ◄
        if self.direction == 2:
            return colored("◄", color)
        elif self.direction == 4:
            return colored("▲", color)
        elif self.direction == 6:
            return colored("►", color)
        else:
            return colored("▼", color)


class AssemblingMachine (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)
        self.recipe = dictionary_entity["recipe"]
        # TODO: Check that it exist

        self.offsets = [
            [0, 0],
            [0, 1],
            [0, -1],
            [1, 1],
            [1, 0],
            [1, -1],
            [-1, 1],
            [-1, 0],
            [-1, -1],
        ]

    def to_char(self, offset=[0, 0]):
        # The entity_offset is used to tell witch part
        # of the assembling machine we want to display
        # For example, if the entity is an assembling machine (3x3 size),
        # the offset will be [0, 0] for the center, [1, 1] for the top-right,
        # [1, -1] for the bottom-right and so on.

        color = "white"
        if self.name == "assembling-machine-2":
            color = "blue"
        if self.name == "assembling-machine-3":
            color = "yellow"

        # ┌─┐
        # │A│
        # └─┘

        if offset == [0, 0]:
            return colored(self.recipe[0] or "?", color)
        elif offset == [1, 1]:
            return colored("┘", color)
        elif offset == [1, -1]:
            return colored("┐", color)
        elif offset == [-1, 1]:
            return colored("└", color)
        elif offset == [-1, -1]:
            return colored("┌", color)
        elif offset == [0, 1] or offset == [0, -1]:
            return colored("─", color)
        else:
            return colored("│", color)


class Container (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

    def to_char(self, offset=[0, 0]):
        return "⧈"


class UndergroundBelt (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

    def to_char(self):
        color = "white"
        if self.name == "underground-belt":
            color = "yellow"
        if self.name == "fast-underground-belt":
            color = "red"
        if self.name == "express-underground-belt":
            color = "blue"

        # ⇦ ⇨ ⇧
        if self.direction == 2:
            return colored("⇨", color)
        elif self.direction == 4:
            return colored("⇩", color)
        elif self.direction == 6:
            return colored("⇦", color)
        else:
            return colored("⇧", color)

# ↕ ↔
# ╔═╗
# ║ ║
# ╚═╝
