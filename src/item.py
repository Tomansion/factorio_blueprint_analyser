
# -----------------------------------------------------------
# Items class
# Used to calculate bottleneck
# -----------------------------------------------------------


class Item:
    def __init__(self, name, amount, type="item"):
        self.name = name
        self.amount = amount
        self.type = type

    def __str__(self):
        return f"{self.name} ({self.amount})"

    def get_ingame_image_path(self):
        # Item image url
        # To display the entity game image, we will the images
        # from : https://wiki.factorio.com/Category:Game_images

        # We need to transform the entity name to a valid url
        entity_wiki_name = self.name.capitalize().replace('-', '_')

        return f"https://wiki.factorio.com/images/{entity_wiki_name}.png"


class Flow:
    def __init__(self, items, amount):
        self.items = items
        self.amount = amount  # Per min
