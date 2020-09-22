import sys

import clean
import transform


def main(*args):
    print("Preprocessing data")
    transform.preprocess()
    clean.preprocess()
    # integrate
    # select features


if __name__ == "__main__":
    main(*sys.argv[1:])
