import sys

from datetime import datetime


def log(msg):
    msg = "[DEBUG {0}] {1}\n".format(datetime.now(), msg)

    for channel in (sys.stderr,):
        # for channel in (sys.stderr, sys.stdout):
        channel.write(msg)
