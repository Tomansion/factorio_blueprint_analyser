import zlib
import json
import sys
import base64
from termcolor import colored

from factorio_blueprint_analyser import config


def verbose(content, end="\n", level=3):
    # Verbose level
    # 0: no output
    # 1: only errors
    # 2: errors and warnings
    # 3: errors, warnings and info
    if config.config.verbose_level >= level:
        print(content, end=end, file=sys.stderr, flush=True)


def warning(content):
    verbose(colored(f"WARNING: {content}", "yellow"), level=2)


def success(content):
    verbose(colored(f"SUCCESS: {content}", "green"), level=3)


def decode(string):
    return json.loads(zlib.decompress(
        base64.b64decode(string[1:])).decode('utf8'))


def encode(dict):
    return '0' + base64.b64encode(zlib.compress(bytes(json.dumps(dict), 'utf8'))).decode('utf8')
