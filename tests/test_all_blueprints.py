from factorio_blueprint_analyser import blueprint_analyser
from os import listdir

# Profiling
import pytest
import pstats
# import cProfile
# profiler = cProfile.Profile()


config_file_path = "config/config_tests.yaml"
blueprints_path = "tests/blueprints"
blueprints = listdir(blueprints_path)

blueprint_analyser.init(config_dict={"verboseLevel": 0, "displayNetwork": False})

nb_tests_to_do = 20

def test_all_blueprints():
    print("Testing all blueprints")
    # profiler.enable()

    for (i, blueprint) in enumerate(blueprints):
        if i >= nb_tests_to_do:
            break

        print(
            f"  === Analysing blueprint: {blueprint}, {i+1}/{len(blueprints)}")
        blueprint_path = f"{blueprints_path}/{blueprint}"

        blueprint_analyser.analyse_blueprint_from_path(blueprint_path)

    # profiler.disable()
    # stats = pstats.Stats(profiler)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.dump_stats(filename="stats.prof")
