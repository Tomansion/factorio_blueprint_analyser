import os
import pathlib

config = None

# Finding where the assets are for when this is installed as a package
parent_path = pathlib.Path(__file__).parent.resolve()

# factorio:
#   # Inserter_capacity_bonus
#   # number between 0 and 7
#   # (https://wiki.factorio.com/Inserter_capacity_bonus_(research))
#   inserter_capacity_bonus: 0

#   # The facorio data generated from the game files
#   # This default data corresponds to the vanilla game
#   # To set your own data, you can follow our mod guide
#   # (Comming soon)
#   data_file_path: "factorio_blueprint_analyser/assets/factorio_raw/factorio_raw_min.json"

# network:
#   # The alogrithm will displat the
#   # results on a web page in a node network
#   # You can disable this feature by setting this to false
#   display: true

# # Verbose level
# # 1: only errors
# # 2: errors and warnings
# # 3: errors, warnings and info
# verbose_level: 3


class Config:
    # Factorio
    inserter_capacity_bonus = 0
    data_file_path = str(parent_path) + \
        "/assets/factorio_raw/factorio_raw_min.json"
    # Network
    display_network = True
    # Verbose level
    verbose_level = 3

    def __init__(self, config=None):
        if config:
            if "inserterCapacityBonus" in config:
                bonus = config["inserterCapacityBonus"]
                if type(bonus) is int and 0 <= bonus <= 7:
                    self.inserter_capacity_bonus = bonus
                else:
                    print(
                        f"Config warning: Invalid inserterCapacityBonus value: {bonus}. The value must be an \
                        integer between 0 and 7. Using default value: {self.inserter_capacity_bonus}")

            if "dataFilePath" in config:
                path = config["dataFilePath"]
                if os.path.exists(path):
                    self.data_file_path = path
                else:
                    print(
                        f"Config warning: Invalid dataFilePath value: {path}. The file does not exist.\
                             Using default value: {self.data_file_path}")

            if "displayNetwork" in config:
                if type(config["displayNetwork"]) is bool:
                    self.display_network = config["displayNetwork"]
                else:
                    print(
                        f"Config warning: Invalid displayNetwork value: {config['displayNetwork']}. \
                            The value must be a boolean. Using default value: {self.display_network}")

            if "verboseLevel" in config:
                level = config["verboseLevel"]
                if type(level) is int and 0 <= level <= 3:
                    self.verbose_level = level
                else:
                    print(
                        f"Config warning: Invalid verboseLevel value: {level}. The value must be an \
                        integer between 0 and 3. Using default value: {self.verbose_level}")


def load_config(config_dict):
    global config
    config = Config(config_dict)
