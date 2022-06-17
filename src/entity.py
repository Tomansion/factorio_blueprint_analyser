from src import utils, factorio


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

        # Check that the entity exists in the Factorio data
        if self.name not in factorio.entities:
            print(f"ERROR: entity {self.name} not found in Factorio data")
            sys.exit(1)

        self.entity_data = factorio.entities[self.name]

    def __str__(self):
        return f"{self.number} {self.name} [{self.position['x']}, {self.position['y']}] [{self.original_position['x']}, {self.original_position['y']}]"

    def to_char(self):
        # ← ↑ → ↓
        # ► ▼ ▲ ◄
        # ↕ ↔
        # ⇦ ⇨ ⇧ ⇩
        # ┌─┐
        # │ │
        # └─┘
        # ╔═╗
        # ║ ║
        # ╚═╝

        if self.entity_data["type"] == "transport-belt":
            if self.direction == 2:
                return "→"
            elif self.direction == 4:
                return "↓"
            elif self.direction == 6:
                return "←"
            else:
                return "↑"

        if self.entity_data["type"] == "inserter":
            if self.direction == 2:
                return "◄"
            elif self.direction == 4:
                return "▲"
            elif self.direction == 6:
                return "►"
            else:
                return "▼"

        return '?'
