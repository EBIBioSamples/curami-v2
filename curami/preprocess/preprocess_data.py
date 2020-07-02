import sys

import clean
import transform
import integrate
import select


def main(*args):
    print("Preprocessing data")
    transform.preprocess()
    clean.preprocess()
    integrate.integrate()
    # select features


if __name__ == "__main__":
    main(*sys.argv[1:])
