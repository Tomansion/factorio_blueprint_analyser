
from factorio_blueprint_analyser import factorio, item, utils

# -----------------------------------------------------------
# Assembly machines recipe class
# -----------------------------------------------------------
DIFFICULTY = "normal"


def get_recipe(name):
    # Check that the recipe exists
    if name not in factorio.recipies:
        utils.warning(f"No recipe found for {name}")
        return None

    return Recipe(name)


class Recipe:
    def __init__(self, name) -> None:
        self.name = name

        factorio_recipe = factorio.recipies[name]

        # Get result item
        nb_item_output = factorio_recipe["result_count"] \
            if "result_count" in factorio_recipe else 1

        self.result = item.Item(name, nb_item_output)
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
                        item.Item(ingredient[0],
                                  ingredient[1]))

                elif isinstance(ingredient, dict):
                    if "type" in ingredient and ingredient["type"] == "fluid":
                        # Fluid ingredient, we ignore it
                        continue

                    self.ingredients.append(
                        item.Item(ingredient["name"],
                                  ingredient["amount"],
                                  type=ingredient["type"]))
            except KeyError:
                utils.warning(f"Something went wrong with the recipe {name}")
                self.exists = False
                return

        # Get production time
        self.time = factorio_recipe["energy_required"] \
            if "energy_required" in factorio_recipe \
            else 1

    def ingredient_required(self, ingredient_name):
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                return True

        return False

    def get_ingredient_nb(self, ingredient_name):
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                return ingredient.amount

        return None

    def all_ingredients_required(self, given_ingredients):
        for ingredient in self.ingredients:
            if ingredient.name not in given_ingredients:
                return False

        return True

    def get_ingame_image_path(self):
        # Item image url
        # To display the entity game image, we will the images
        # from : https://wiki.factorio.com/Category:Game_images

        # We need to transform the entity name to a valid url
        entity_wiki_name = self.name.capitalize().replace('-', '_')

        return f"https://wiki.factorio.com/images/{entity_wiki_name}.png"

    def __str__(self) -> str:
        ingredients_str = ", ".join(
            [f"{item.name}: {item.amount}" for item in self.ingredients])
        return f"{self.name} [{ingredients_str}] => ({self.result})"
