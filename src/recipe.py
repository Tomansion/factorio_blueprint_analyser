
from src import factorio, item

# -----------------------------------------------------------
# Assembly machines recipe class
# -----------------------------------------------------------
DIFFICULTY = "normal"


class Recipe:
    def __init__(self, name) -> None:
        self.name = name
        self.exists = True

        # Check that the recipe exists
        if name not in factorio.recipies:
            print(f"WARNING: no recipe found for {name}")
            self.exists = False
            return

        factorio_recipe = factorio.recipies[name]

        # Get result item
        self.nb_item_output = factorio_recipe["result_count"] \
            if "result_count" in factorio_recipe else 1

        self.result = item.Item(name, self.nb_item_output)
        # TODO: deal with multiple results

        # Get ingredients
        self.ingredients = []

        ingredients = factorio_recipe[DIFFICULTY]["ingredients"] \
            if DIFFICULTY in factorio_recipe \
            else factorio_recipe["ingredients"]

        for ingredient in ingredients:
            # The recipe ingredients can have two formats:
            # - ['fast-transport-belt', 1]
            # - {'amount': 20, 'type': 'fluid', 'name': 'lubricant'}

            try:
                if isinstance(ingredient, list):
                    self.ingredients.append(
                        item.Item(ingredient[0], ingredient[1]))

                elif isinstance(ingredient, dict):
                    self.ingredients.append(
                        item.Item(ingredient["name"], ingredient["amount"]))
            except KeyError:
                print(f"WARNING: Something went wrong with the recipe {name}")
                self.exists = False
                return

        # Get production time
        self.time = factorio_recipe["energy_required"] \
            if "energy_required" in factorio_recipe \
            else 1

    def get_ingame_image_path(self):
        # Item image url
        # To display the entity game image, we will the images
        # from : https://wiki.factorio.com/Category:Game_images

        # We need to transform the entity name to a valid url
        entity_wiki_name = self.name.capitalize().replace('-', '_')

        return f"https://wiki.factorio.com/images/{entity_wiki_name}.png"
