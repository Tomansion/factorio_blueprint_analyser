
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

        if amount is None:
            print(f"WARNING: Flow {self} has no amount")
            # TODO: Remove this, it crash on the bp beltFac4.txt
            self.amount = 0

        if items is None or len(items) == 0:
            print(f"ERROR: a flow was created without items")
            raise Exception("Flow without items")

    def __str__(self) -> str:
        items = ""
        for item in self.items:
            items += f"{item.name} "
        return f"[{items} {self.amount}/min]"


def merge_flows(flows):
    # Fuse all flows
    total_ips = 0
    treated_items = []
    treated_items_names = []
    for flow in flows:
        total_ips += flow.amount
        for item in flow.items:
            if item.name not in treated_items_names:
                treated_items_names.append(item.name)
                treated_items.append(Item(item.name, 1))

    # Create a new flow
    return Flow(treated_items, total_ips)
