from math import floor
from termcolor import colored

from factorio_blueprint_analyser import factorio, recipe, utils, config

# -----------------------------------------------------------
# Base class for all entities
# The create_entity function will return an entity instance
# corresponding to the givenentity_in_blueprint
# -----------------------------------------------------------


def create_entity(entity_in_blueprint, virtual=False):
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
        utils.warning(f"Entity {entity_in_blueprint['name']} not found in Factorio data")
        # sys.exit(1)
        return None

    entity_data = factorio.entities[entity_in_blueprint["name"]]

    # Virtual entities are entities that are not in the original blueprint
    # We have created them to solve certain edge cases such as the inserter
    # that needs to pickup the item from an empty tile
    entity_data["virtual"] = virtual

    # Return the corresponding Entity object
    if entity_data["type"] == "transport-belt":
        return TransportBelt(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "assembling-machine":
        return AssemblingMachine(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "inserter":
        if entity_data["name"] == "long-handed-inserter":
            return RedArm(entity_in_blueprint, entity_data)
        elif entity_data["name"] == "stack-inserter":
            return StackInserter(entity_in_blueprint, entity_data)
        else:
            return Inserter(entity_in_blueprint, entity_data)

    elif entity_data["type"] in ["container", "logistic-container"]:
        return Container(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "underground-belt":
        return UndergroundBelt(entity_in_blueprint, entity_data)

    elif entity_data["type"] == "splitter":
        return Splitter(entity_in_blueprint, entity_data)

    utils.warning(f"entity {entity_in_blueprint['name']} of type {entity_data['type']} not supported")


# Enities interfaces
class Entity:
    def __init__(self, entity_in_blueprint, entity_data):
        self.data = entity_data
        self.number = entity_in_blueprint["entity_number"]
        self.name = entity_in_blueprint["name"]
        self.large = False

        # Correc position
        self.original_position = entity_in_blueprint["position"]
        self.position = [
            floor(entity_in_blueprint["position"]["x"]),
            floor(entity_in_blueprint["position"]["y"])
        ]

        # Get the direction
        if "direction" in entity_in_blueprint:
            self.direction = entity_in_blueprint["direction"]
        else:
            self.direction = None

        self.speed = None

    def __str__(self):
        speed = ""
        if self.speed is not None:
            speed = f"{self.speed}/s"

        return f"{self.number} {self.name} [{self.position[0]}, {self.position[1]}] {self.to_char()} {speed}"

    def to_char(self):
        return '?'

    def get_ingame_image_path(self):
        # Item image url
        # To display the entity game image, we will the images
        # from : https://wiki.factorio.com/Category:Game_images

        # We need to transform the entity name to a valid url
        entity_wiki_name = self.data['name'].capitalize().replace('-', '_')

        return f"https://wiki.factorio.com/images/{entity_wiki_name}.png"


class LargeEntity(Entity):
    # Assembling machines, splitters, furnace, etc.
    def __init__(self, entity_in_blueprint, entity_data):
        super().__init__(entity_in_blueprint, entity_data)
        self.large = True
        self.offsets = []

    def to_char(self, coords=[0, 0]):
        return '?'

    def can_connect_to(self, entity):
        # Check if the entity can be connected to this entity
        # For example, a belt can be connected to an other belt
        return False


# Factorio entities:
class TransportBelt(Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

        # Saving speed of the belt
        if "speed" not in entity_data:
            utils.warning(f"{self.name} has no speed")
            self.tile_per_sec = 0.03125  # the tile_per_sec of the lvl1 transport belt
        else:
            self.tile_per_sec = entity_data["speed"]

        # Calculation of the belt item per second
        # 60 ticks / second
        # A tile is 4 items
        # There is two line on the belt
        # this will result, for the first belt, with an output of 15 item per second
        # This can be veryfied here: https://wiki.factorio.com/Belt_transport_system

        self.speed = self.tile_per_sec * 60 * 4 * 2

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
        elif self.direction is None:
            return colored("↑", color)

        return colored("?", color)

    def get_tile_in_front_offset(self):
        # Returns an offset of the tile
        # in front of the conveyor belt
        #   example: [1, 0] if the conveyor is facing the right

        if self.direction == 2:
            return [1, 0]
        elif self.direction == 4:
            return [0, 1]
        elif self.direction == 6:
            return [-1, 0]
        elif self.direction is None:
            return [0, -1]

    def can_connect_to(self, entity):
        if entity.data["type"] == "transport-belt":
            # A belt can be connected to another belt
            # except if they are facing each other
            if self.direction == 2 and entity.direction == 6 or \
                    self.direction == 6 and entity.direction == 2:
                return False
            elif self.direction == 4 and entity.direction is None or \
                    self.direction is None and entity.direction == 4:
                return False

            return True

        elif entity.data["type"] == "underground-belt" and \
                entity.belt_type == "input" or \
                entity.data["type"] == "splitter":
            # A belt can be connected to an underground belt
            # except if they are facing each other

            # return self.direction == entity.direction

            if self.direction == 2 and entity.direction == 6 or \
                    self.direction == 6 and entity.direction == 2:
                return False
            elif self.direction == 4 and entity.direction is None or \
                    self.direction is None and entity.direction == 4:
                return False

            # We are ignoring the complex transfers for now
            return True

        return False


class Inserter (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

        # Saving speed of the inserter
        if "rotation_speed" not in entity_data:
            utils.warning(f"{self.name} has no rotation speed")
            self.rotation_speed = 0.014  # the rotation_speed of the lvl1 inserter
        else:
            self.rotation_speed = entity_data["rotation_speed"]

        # The rotation speed is the turn per tick
        # There is 60 ticks per second
        self.speed = self.rotation_speed * 60  # turn or items per second

        # Inserter capacity bonnus https://wiki.factorio.com/Inserter_capacity_bonus_(research)
        if config.config.inserter_capacity_bonus >= 7:
            self.speed *= 3
        elif config.config.inserter_capacity_bonus >= 2:
            self.speed *= 2

    def get_drop_tile_offset(self):
        # Returns an offset of the tile where items are dropped
        #   example: [1, 0] if the arm is facing the right
        # For some reason, the inserter is facing
        # the oposite direction compared to the belts
        if self.direction == 2:
            return [-1, 0]
        elif self.direction == 4:
            return [0, -1]
        elif self.direction == 6:
            return [1, 0]
        else:
            return [0, 1]

    def get_drop_tile_coord(self):
        # Returns the coordinaties of the tile where items are dropped
        pickup_tile_offset = self.get_drop_tile_offset()
        return [
            pickup_tile_offset[0] + self.position[0],
            pickup_tile_offset[1] + self.position[1]
        ]

    def get_pickup_tile_offset(self):
        # Returns the offset of the tile where items are picked up
        return [
            -self.get_drop_tile_offset()[0],
            -self.get_drop_tile_offset()[1]
        ]

    def get_pickup_tile_coord(self):
        # Returns the coordinates of the tile where items are picked up
        pickup_tile_offset = self.get_pickup_tile_offset()
        return [
            pickup_tile_offset[0] + self.position[0],
            pickup_tile_offset[1] + self.position[1]
        ]

    def can_move_to(self, entity):
        # The arm can move items to belts,
        # underground belts, chests or assembling machines
        available_types = ["transport-belt",
                           "underground-belt",
                           "container",
                           "logistic-container",
                           "assembling-machine",
                           "splitter"]

        if entity.data["type"] in available_types:
            return True

        return False

    def can_move_from(self, entity):
        # The arm can move items from belts,
        # underground belts, chests or assembling machines

        # It seams that the allowed entities
        # are the same as the can_move_to
        return self.can_move_to(entity)

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


class StackInserter  (Inserter):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

        # Rewriting the speed
        self.speed = self.rotation_speed * 60  # turn or items per second

        # Inserter capacity bonnus https://wiki.factorio.com/Inserter_capacity_bonus_(research)
        capacity_multiplier = 2 + config.config.inserter_capacity_bonus

        if config.config.inserter_capacity_bonus >= 5:
            capacity_multiplier += 1
        if config.config.inserter_capacity_bonus >= 6:
            capacity_multiplier += 1
        if config.config.inserter_capacity_bonus >= 7:
            capacity_multiplier += 1

        self.speed *= capacity_multiplier


class RedArm (Inserter):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

    def get_drop_tile_offset(self):
        return [e * 2 for e in super().get_drop_tile_offset()]

    def get_ingame_image_path(self):
        # This entity image path is an exception
        return "https://wiki.factorio.com/images/Long-handed_inserter.png"


class AssemblingMachine (LargeEntity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

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

        self.recipe = None
        if "recipe" in dictionary_entity:
            self.recipe = recipe.get_recipe(dictionary_entity["recipe"])

        if self.recipe is not None:
            # Saving speed of the assembling machine
            if "crafting_speed" not in entity_data:
                utils.warning(f"{self.name} has no crafting speed", level=1)
                self.speed = 0.5  # the speed of the assembling-machine-1
            else:
                self.speed = entity_data["crafting_speed"]

            time_per_item = self.recipe.time / self.speed
            self.items_per_second = self.recipe.result.amount / time_per_item

            # Define the required items per second
            # to have the assembling machine working at 100%
            self.required_items_per_second = {}
            for item in self.recipe.ingredients:
                self.required_items_per_second[item.name] = item.amount / \
                    time_per_item

    def get_usage_ratio(self, ingredients_amount):
        # Calculate the number of items produced per second
        # according to an ingredients amount dictionary

        if self.recipe is None or not self.recipe.all_ingredients_required(ingredients_amount.keys()):
            return 0

        lowest_ingredient_requierment_ratio = None
        for ingredient in ingredients_amount:

            completion_ratio = ingredients_amount[ingredient] / \
                self.required_items_per_second[ingredient]

            if lowest_ingredient_requierment_ratio is None or \
                    completion_ratio < lowest_ingredient_requierment_ratio:
                lowest_ingredient_requierment_ratio = completion_ratio

        return min(1.0, lowest_ingredient_requierment_ratio)

    def to_char(self, coords=None):
        color = "white"
        if self.name == "assembling-machine-2":
            color = "blue"
        if self.name == "assembling-machine-3":
            color = "yellow"

        if coords is None:
            return colored(self.recipe.name[0] if self.recipe is not None else "?", color)

        offset = [coords[0] - self.position[0],
                  coords[1] - self.position[1]]

        # The entity_offset is used to tell witch part
        # of the assembling machine we want to display
        # For example, if the entity is an assembling machine (3x3 size),
        # the offset will be [0, 0] for the center, [1, 1] for the top-right,
        # [1, -1] for the bottom-right and so on.

        # ┌─┐
        # │A│
        # └─┘

        if offset == [0, 0] or coords is None:
            return colored(self.recipe.name[0] if self.recipe is not None else "?", color)
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

    def __str__(self):
        recipe_str = ""
        if self.recipe is not None:
            recipe_str = self.recipe.name

        return super().__str__() + " [" + recipe_str + "]"


class Container (Entity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

    def to_char(self):
        if self.name == "logistic-chest-passive-provider":
            return colored("⧈", "red")
        elif self.name == "logistic-chest-active-provider":
            return colored("⧈", "magenta")
        elif self.name == "logistic-chest-buffer":
            return colored("⧈", "green")
        elif self.name == "logistic-chest-requester":
            return colored("⧈", "cyan")
        elif self.name == "logistic-chest-storage":
            return colored("⧈", "yellow")

        return "⧈"

    def get_ingame_image_path(self):

        if self.name == "logistic-chest-passive-provider":
            return "https://wiki.factorio.com/images/Passive_provider_chest.png"
        elif self.name == "logistic-chest-active-provider":
            return "https://wiki.factorio.com/images/Active_provider_chest.png"
        elif self.name == "logistic-chest-buffer":
            return "https://wiki.factorio.com/images/Buffer_chest.png"
        elif self.name == "logistic-chest-requester":
            return "https://wiki.factorio.com/images/Requester_chest.png"
        elif self.name == "logistic-chest-storage":
            return "https://wiki.factorio.com/images/Storage_chest.png"

        return super().get_ingame_image_path()


class UndergroundBelt (TransportBelt):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)

        self.belt_type = dictionary_entity["type"]  # "input" or "output"

        # Saving belt distance
        if "max_distance" not in entity_data:
            self.max_distance = 5  # the distance of the lvl1 underground-belt
        else:
            self.max_distance = entity_data["max_distance"]

        # Saving speed
        if "speed" not in entity_data:
            utils.warning(f"{self.name} has no speed")
            self.speed = 0.03125  # the speed of the lvl1 underground-belt
        else:
            self.speed = entity_data["speed"]

        self.speed = self.speed * 60 * 4 * 2

    def get_possible_output_coords(self):
        start_coord = self.position
        possible_coords = []

        for _ in range(self.max_distance):
            start_coord = [
                start_coord[0] + self.get_tile_in_front_offset()[0],
                start_coord[1] + self.get_tile_in_front_offset()[1]
            ]

            possible_coords.append(start_coord)

        return possible_coords

    def to_char(self):
        color = "white"
        if self.name == "underground-belt":
            color = "yellow"
        if self.name == "fast-underground-belt":
            color = "red"
        if self.name == "express-underground-belt":
            color = "blue"

        if self.belt_type == "input":
            # ⇐ ⇑ ⇒ ⇓
            if self.direction == 2:
                return colored("⇒", color)
            elif self.direction == 4:
                return colored("⇓", color)
            elif self.direction == 6:
                return colored("⇐", color)
            else:
                return colored("⇑", color)
        else:
            # ⇦ ⇨ ⇧ ⇩
            if self.direction == 2:
                return colored("⇨", color)
            elif self.direction == 4:
                return colored("⇩", color)
            elif self.direction == 6:
                return colored("⇦", color)
            else:
                return colored("⇧", color)

    def __str__(self):
        return super().__str__() + " " + self.belt_type


class Splitter (LargeEntity):
    def __init__(self, dictionary_entity, entity_data):
        super().__init__(dictionary_entity, entity_data)
        self.offsets = [[0, 0], self.get_second_belt_offset()]
        # TODO: Filters

        # Saving speed
        if "speed" not in entity_data:
            utils.warning(f"{self.name} has no speed")
            self.speed = 0.03125  # the speed of the lvl1 splitter
        else:
            self.speed = entity_data["speed"]

        self.speed = self.speed * 60 * 4 * 2

    def get_second_belt_offset(self):

        if self.direction == 2:  # ⇨
            return [0, -1]
        elif self.direction == 4:  # ⇩
            return [-1, 0]
        elif self.direction == 6:  # ⇦
            return [0, -1]
        else:  # ⇧
            return [-1, 0]

    def get_drop_tile_offsets(self):
        if self.direction == 2:  # ⇨
            return [[1, -1], [1, 0]]
        elif self.direction == 4:  # ⇩
            return [[-1, 1], [0, 1]]
        elif self.direction == 6:  # ⇦
            return [[-1, -1], [-1, 0]]
        else:  # ⇧
            return [[-1, -1], [0, -1]]

    def can_move_to(self, entity):
        if entity.data["type"] == "transport-belt":
            # A belt can be connected to another belt
            # except if they are facing each other
            if self.direction == 2 and entity.direction == 6 or \
                    self.direction == 6 and entity.direction == 2:
                return False
            elif self.direction == 4 and entity.direction is None or \
                    self.direction is None and entity.direction == 4:
                return False

            return True

        elif entity.data["type"] == "underground-belt" and \
                entity.belt_type == "input" or \
                entity.data["type"] == "splitter":
            # A belt can be connected to an underground belt
            # if they are in the same direction

            return self.direction == entity.direction

        return False

    def to_char(self, coords=None):

        color = "white"
        if self.name == "splitter":
            color = "yellow"
        if self.name == "fast-splitter":
            color = "red"
        if self.name == "express-splitter":
            color = "blue"

        # ⬑⬏ ⬐⬎
        # ↱    ↰
        # ↳    ↲

        if coords is None:
            return colored("⬑⬏", color)

        if self.position[0] == coords[0] and self.position[1] == coords[1]:
            if self.direction == 2:
                return colored("↳", color)
            elif self.direction == 4:
                return colored("⬎", color)
            elif self.direction == 6:
                return colored("↲", color)
            else:
                return colored("⬏", color)
        else:
            if self.direction == 2:
                return colored("↱", color)
            elif self.direction == 4:
                return colored("⬐", color)
            elif self.direction == 6:
                return colored("↰", color)
            else:
                return colored("⬑", color)


# ↕ ↔
# ╔═╗
# ║ ║
# ╚═╝

# ⭦ ⭧ ⭩ ⭨
