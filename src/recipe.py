
from src import factorio

# -----------------------------------------------------------
# Assembly machines recipe class
# -----------------------------------------------------------


class Recipe:
    def __init__(self, name) -> None:
        self.name = name

        # Check that the recipe exists
        if name not in factorio.recipies:
            print(f"WARNING: no recipe found for {name}")
            self.exists = False
        else:
            self.ingredients = factorio.recipies[name]
            print(self.ingredients)

    def get_ingame_image_path(self):
        # Item image url
        # To display the entity game image, we will the images
        # from : https://wiki.factorio.com/Category:Game_images

        # We need to transform the entity name to a valid url
        entity_wiki_name = self.name.capitalize().replace('-', '_')

        return f"https://wiki.factorio.com/images/{entity_wiki_name}.png"
