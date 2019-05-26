#!/usr/bin/env python3
import sys
import json
import time
import urllib.request
import random
import pprint
import sys

from common import *


def main():
    Print.blue(TerminalColors.bold("EUROPARLAMENTARE"))
    euro_data = process_json_data(download_json_data(PAGE_EURO))
    euro_data.print()
    Print.newlines()

    Print.blue(TerminalColors.bold("REFERENDUM"))
    referendum_data = process_json_data(download_json_data(PAGE_REFERENDUM))
    referendum_data.print()
    Print.newlines()

    Print.blue(TerminalColors.bold("Difference (EURO - REFERENDUM)"))
    difference_data = euro_data - referendum_data
    difference_data.print()

if __name__ == "__main__":
    main()
