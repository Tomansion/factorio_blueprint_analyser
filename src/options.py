import io
import argparse
import sys
import os
import shutil

from src import utils

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
                        help="Blueprint book file path", default="./example_blueprint_books/general")

    parser.add_argument("-o", "--output", nargs="?", dest="output",
                        help="Folder output for the json", default="blueprint_book_json")

    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force overwrite of existing output folder", default=False)

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

    # Add trailing slash to output folder if not present
    if not opt.output.endswith("/"):
        opt.output += "/"

    # Check if the output folder exists
    if os.path.exists(opt.output):
        if not opt.force:
            print(f"Output folder '{opt.output}' already exists")
            print("Use --force or -f to overwrite it")
            sys.exit(1)
        else:
            shutil.rmtree(opt.output)
            os.mkdir(opt.output)
    else:
        os.mkdir(opt.output)

    utils.verbose(f"file: {opt.input}")

    utils.verbose(silent, input, output, force)
