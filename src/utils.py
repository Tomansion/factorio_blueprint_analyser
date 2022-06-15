import zlib
import json
import sys
import base64

from src import options


def verbose(*args):
    if not options.silent:
        print(*args, file=sys.stderr, flush=True)


def decode(string):
    return json.loads(zlib.decompress(
        base64.b64decode(string[1:])).decode('utf8'))


def encode(dict):
    return '0' + base64.b64encode(zlib.compress(bytes(json.dumps(dict), 'utf8'))).decode('utf8')
