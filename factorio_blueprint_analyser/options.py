import io
import argparse
import sys
import os

# -----------------------------------------------------------
# Read the user input and check the options
# The options are stored in the global variables
# -----------------------------------------------------------

input = ""
output = ""
force = False
config_path = ""


def read_options():
    global input, output, force, config_path

    # ==== Options read ====

    sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding="utf-8")
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Find the bottleneck in a Factorio blueprint")

    parser.add_argument("-i", "--input", nargs="?", dest="input",
                        help="Blueprint JSON or encoded file path", default="./examples/beltFac.json")

    parser.add_argument("-o", "--output", nargs="?", dest="output",
                        help="JSON File output for the analysed blueprint", default="analysed_blueprint.json")

    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force overwrite of existing result file", default=False)

    parser.add_argument("-c", "--config", nargs="?", dest="config",
                        help="Analyser yaml config file path", default="config/config_default.yaml")

    opt = parser.parse_args()

    input = opt.input
    output = opt.output
    force = opt.force
    config_path = opt.config

    # ==== Options validation ====

    # Check if the input file exists
    if not os.path.exists(opt.input):
        raise Exception(f"Input file '{opt.input}' does not exist")

    # Check if the output file exists
    if os.path.exists(opt.output) and not force:
        raise Exception(
            f"Output file '{opt.output}' already exists\nUse --force or -f to overwrite it")

    # Check if the config file exists
    if not os.path.exists(opt.config):
        raise Exception(f"Config file '{opt.config}' does not exist")
