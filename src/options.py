import io
import argparse
import sys
import os

from src import utils

# -----------------------------------------------------------
# Read the user input and check the options
# The options are stored in the global variables
# -----------------------------------------------------------

silent = False
input = ""
output = ""
force = False


def read_options():
    global silent, input, output, force

    # ==== Options read ====

    sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding="utf-8")
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Convert a factorio blueprint book to json")

    parser.add_argument("-s", "--silent", action="store_true", dest="silent",
                        help="Stop verbose output on STDERR", default=False),

    parser.add_argument("-i", "--input", nargs="?", dest="input",
                        help="Blueprint JSON or encoded file path", default="./examples/beltFac.json")

    parser.add_argument("-o", "--output", nargs="?", dest="output",
                        help="JSON File output for the analysed blueprint", default="analysed_blueprint.json")

    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force overwrite of existing result file", default=False)

    opt = parser.parse_args()

    silent = opt.silent
    input = opt.input
    output = opt.output
    force = opt.force

    # ==== Options validation ====

    # Check if the input file exists
    if not os.path.exists(opt.input):
        print(f"Input file '{opt.input}' does not exist")
        sys.exit(1)

    # Check if the output file exists
    if os.path.exists(opt.output) and not force:
        print(f"Output file '{opt.output}' already exists")
        print("Use --force or -f to overwrite it")
        sys.exit(1)

    utils.verbose(f"file: {opt.input}")
