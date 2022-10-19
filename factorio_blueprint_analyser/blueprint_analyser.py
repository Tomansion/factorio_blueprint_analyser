
from factorio_blueprint_analyser import (
    factorio,
    blueprint,
    network,
    config
)

def init(config_dict=None):
    # Init config
    config.load_config(config_dict)

    # Load the Factorio data
    factorio.load_data()


def analyse_blueprint(blueprint_string):
    bp = blueprint.load_blueprint(blueprint_string)
    return _process_blueprint(bp)


def analyse_blueprint_from_path(blueprint_path):
    bp = blueprint.load_blueprint_from_path(blueprint_path)
    return _process_blueprint(bp)


def _process_blueprint(bp):
    bp.display()

    # Creade a node network from the blueprint
    nw = network.create_network(bp)

    # Calculate bottleneck
    nw.calculate_bottleneck()
    if config.config.display_network:
        nw.display()

    # Export the analysis
    analysis_result = bp.get_analysis()

    return analysis_result
