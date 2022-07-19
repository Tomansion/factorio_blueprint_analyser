
from src import (
    factorio,
    blueprint,
    network,
    config
)


def calculate_blueprint_bottleneck(blueprint_path, config_path=None):
    # Init config
    config.load_config(config_path)

    # Load the Factorio data
    factorio.load_data()

    # Read the input blueprint
    bp = blueprint.load_blueprint(blueprint_path)
    bp.display()

    # Creade a node network from the blueprint
    nw = network.create_network(bp)

    # Calculate bottleneck
    nw.calculate_bottleneck()
    # if config.config.display_network:
    #     nw.display()

    # Export the analysis
    return bp.get_analysis()
