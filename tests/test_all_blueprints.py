from src import blueprint_analyser
from os import listdir

config_file_path = "config/config_tests.yaml"

blueprints_path = "tests/blueprints"
blueprints = listdir(blueprints_path)


def test_all_blueprints():
    for (i, blueprint) in enumerate(blueprints):
        try:
            print(f"Analysing blueprint: {blueprint}, {i+1}/{len(blueprints)}")
            blueprint_path = f"{blueprints_path}/{blueprint}"
            blueprint_analyser.calculate_blueprint_bottleneck(
                blueprint_path, config_path=config_file_path)

        except Exception as e:
            print(f"Error: {e}")
