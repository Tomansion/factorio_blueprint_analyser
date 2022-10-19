import yaml
import os

# Default config YAML format:
#
#   factorio:
#     difficulty: normal
#     inserter_capacity_bonus: 0
#     data_file_path: "factorio_blueprint_analyser/assets/factorio_raw/factorio_raw_min.json"
#   verbose_level: 3
#   network:
#     display: true

default_config_path = "config/config_default.yaml"
config = None


class Config:
    config = None

    def __init__(self, config_path=None):
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        # Check if the default config file exists
        if not os.path.exists(default_config_path):
            raise FileNotFoundError(
                f"The default config file '{default_config_path}' does not exist")

        with open(default_config_path, "r") as ymlfile:
            default_config = yaml.load(ymlfile)

        if config_path is None:
            return default_config

        # Check if the default config file exists
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"The config file '{config_path}' does not exist")

        with open(config_path, "r") as ymlfile:
            cfg = yaml.load(ymlfile)

        # Merge the default config with the user config
        for key in cfg:
            if key in default_config:
                default_config[key] = cfg[key]
            else:
                print(f"Warning: Unknown config key: {key}")

        return default_config

    def get_config_value(self, *args):
        conf = self.config

        for arg in args:
            if arg not in conf:
                raise KeyError(
                    f"Couldn't find the config key: {args.join('.')}")

            conf = conf[arg]

        return conf

    # Factorio
    @property
    def inserter_capacity_bonus(self):
        return self.get_config_value("factorio", "inserter_capacity_bonus")

    @property
    def difficulty(self):
        return self.get_config_value("factorio", "difficulty")

    @property
    def data_file_path(self):
        return self.get_config_value("factorio", "data_file_path")

    # Verbose level
    @property
    def verbose_level(self):
        return self.get_config_value("verbose_level")

    # Network
    @property
    def display_network(self):
        return self.get_config_value("network", "display")


def load_config(config_path=None):
    global config
    config = Config(config_path)
