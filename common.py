#!/usr/bin/env python3
import sys
import json
import time
import urllib.request
import random
import pprint
import sys
from socket import timeout

PAGE_EURO = "https://prezenta.bec.ro/europarlamentare26052019"
PAGE_REFERENDUM = "https://prezenta.bec.ro/referendum26052019"


# 18.267.997
MAX_VOTES = 18267997

MAX_VOTES_OUTSIDE = 18968840

class TerminalColors:
    HEADER = '\033[95m'

    BOLD = '\033[;1m'

    BLUE = '\033[0;36m'
    BLUE_LIGHT = '\033[1;36m'

    GREEN = '\033[0;32m'
    GREEN_LIGHT = '\033[1;32m'

    YELLOW = '\033[0;33m'
    YELLOW_LIGHT = '\033[1;33m'

    RED = '\033[0;31m'
    RED_LIGHT = '\033[1;31m'

    # No Color
    END = '\033[0m'
    RESET = END

    @classmethod
    def bold(cls, text):
        if Print.can_use_colors():
            return cls.BOLD + str(text) + cls.END

        return text

class Print:
    @classmethod
    def _print_internal(cls, color, string, **kwargs):
        if cls.can_use_colors():
            # You're running in a real terminal
            prefix, suffix = color, TerminalColors.END
        else:
            # You're being piped or redirected
            prefix, suffix = '', ''

        print(prefix + string + suffix, **kwargs)

        # Flush because some consoles are retarded
        cls.flush()

    @classmethod
    def _print_internal_args(cls, color, *args, **kwargs):
        cls._print_internal(color, " ".join(map(str, args)), **kwargs)

    @classmethod
    def flush(cls):
        sys.stdout.flush()

    # You're running in a real terminal
    @classmethod
    def can_use_colors(cls):
        return sys.stdout.isatty()

    @classmethod
    def newlines(cls, nr = 1):
        if nr > 0:
            print('\n' * nr, end='')

    @classmethod
    def reset_color(cls):
        if cls.can_use_colors():
            print(TerminalColors.RESET)

    @classmethod
    def red(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.RED, *args, **kwargs)

    @classmethod
    def red_light(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.RED_LIGHT, *args, **kwargs)

    @classmethod
    def blue(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.BLUE, *args, **kwargs)

    @classmethod
    def blue_light(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.BLUE_LIGHT, *args, **kwargs)

    @classmethod
    def yellow(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.YELLOW, *args, **kwargs)

    @classmethod
    def yellow_light(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.YELLOW_LIGHT, *args, **kwargs)

    @classmethod
    def green(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.GREEN, *args, **kwargs)

    @classmethod
    def green_light(cls, *args, **kwargs):
        cls._print_internal_args(TerminalColors.GREEN_LIGHT, *args, **kwargs)

    @classmethod
    def config_value(cls, config_name, config_value, seperator=" = ", prefix='\t'):
        cls.blue("{}{}{}".format(prefix, config_name, seperator), end='')
        cls.blue_light(config_value)

    @classmethod
    def format_pretty(cls, obj, indent=1, width=80, depth=None):
        return pprint.pformat(obj, indent=indent, width=width, depth=depth)


class VotesData:
    def __init__(self):
        self.counties = dict()
        self.max_voters = 0
        self.total_voters = 0
        self.total_voters_rural = 0
        self.total_voters_urban = 0
        self.presence = 0.0

        self.is_difference = False
        self.counties_difference = []

    def str_max_voters(self):
        return "{:,}".format(self.max_voters)

    def str_total_voters(self):
        return "{:,}".format(self.total_voters)

    def str_total_voters_urban(self):
        return "{:,}".format(self.total_voters_urban)

    def str_total_voters_rural(self):
        return "{:,}".format(self.total_voters_rural)

    def str_presence(self):
        return "{0:.2f}%".format(self.presence)

    def print(self, cli=True):
        tabs = "\t" * 1

        if cli:
            Print.blue_light("Voters:")
        else:
            print("Voters")

        print(tabs + "Total = {}".format(self.str_total_voters()))
        print(tabs + "Urban = {}".format(self.str_total_voters_urban()))
        print(tabs + "Rural = {}".format(self.str_total_voters_rural()))

        print("Presence = {}".format(self.str_presence()))

    def __sub__(self, other):
        difference = VotesData()
        difference.is_difference = True
        difference.total_voters = self.total_voters - other.total_voters
        difference.total_voters_rural = self.total_voters_rural - other.total_voters_rural
        difference.total_voters_urban = self.total_voters_urban - other.total_voters_urban
        difference.presence = self.presence - other.presence

        # Difference in counties
        for county_code in self.counties:
            if county_code not in other.counties:
                continue

            self_county = self.counties[county_code]
            other_county =  other.counties[county_code]

            self_county_total = self_county['voters_rural'] + self_county["voters_urban"]
            other_county_total = other_county['voters_rural'] + other_county["voters_urban"]

            difference.counties_difference.append({
                "code": county_code,
                "name": self_county["name"],
                "presence": self_county['presence'] - other_county['presence'],
                "presence_str": "{0:.2f}%".format(self_county['presence'] - other_county['presence']),
                "max_voters": self_county["max_voters"],
                "voters_rural": "{:,}".format(self_county['voters_rural'] - other_county['voters_rural']),
                "voters_urban": "{:,}".format(self_county["voters_urban"] - other_county["voters_urban"]),
                "voters_total": "{:,}".format(self_county_total - other_county_total)
            })

        # Sort
        difference.counties_difference.sort(key=lambda county: county["presence"], reverse=True)
        return difference

class BECTimeoutException(Exception):
    pass

def download_page(url):
    try:
        response = urllib.request.urlopen(url, timeout=20)
        data = response.read()

    except urllib.error.URLError:
        raise BECTimeoutException("BEC site is down, most likely.")
    except timeout:
        raise BECTimeoutException("BEC site is down, most likely.")

    return data.decode('utf-8');


def get_download_timestamp():
    return "{}{}".format(int(time.time()), random.randint(1000, 9999))


def download_json_data(url):
    data = download_page("{}/data/presence/json/presence_SR_now.json?_={}".format(url, get_download_timestamp()))
    return json.loads(data)


def process_json_data(raw_dict_data):
    # Print.blue_light("process_json_data")

    data = VotesData()
    for county in raw_dict_data["county"]:

        # Remove expats
        if county["county_code"] == "SR":
            continue

        # Map from county code to data
        data.counties[county["county_code"]] = {
            "name": county["county_name"],
            "max_voters": county["initial_count"],
            "voters_rural": county["medium_r"],
            "voters_urban": county["medium_u"],
            "presence": county["presence"]
        }

        # Calculate totals
        # data.max_voters += county["initial_count"]
        data.total_voters_rural += county["medium_r"]
        data.total_voters_urban += county["medium_u"]
        data.total_voters = data.total_voters_rural + data.total_voters_urban

        # print(county["county_name"])
        # total_alternative = county["LT"]
        # total_urban_rural =  county["medium_r"] + county["medium_u"]
        # print(total_alternative, total_urban_rural, total_alternative == total_urban_rural)


    # calculate total expats
    # for precinct in raw_dict_data["precinct"]:
    #     if precinct["county_code"] != "SR":
    #         continue

    # NOTE because we also include the expats we must use the total population number
    data.max_voters = MAX_VOTES
    data.presence = data.total_voters / data.max_voters  * 100
    difference = MAX_VOTES - data.max_voters
    # if difference != 0:
        # Print.yellow("Difference between UI and data in total voters:", difference)

    return data
