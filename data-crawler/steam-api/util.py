# -*- coding: utf-8 -*-

import requests
import os
import time
import datetime


# === Constants ===
APP_LIST_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
APP_URL_PREFIX = "http://store.steampowered.com/api/appdetails?appids="
WAITTING_TIME = 10  # in seconds
APPS_PER_REQUEST = 200  # The length of URL should be under 2000 characters


# === Predefined functions ===


def log_warning(msg):
    print("\033[93m[WARNING] %s\033[0m" % msg.encode())


def log_info(msg):
    print("[INFO] %s" % msg.encode())


def log_fine(msg):
    print("\033[92m[FINE] %s\033[0m" % msg.encode())


def log_debug(msg):
    print("\033[94m[DEBUG] %s\033[0m" % msg.encode())


def ensure_path(path):
    if not os.path.exists(path):
        log_warning("Can't not find output directory '%s', Create a new one" % path)
        os.makedirs(path)


def retrieve_data(url):

    # Wait 1 second before sending a request (1 request per second rule)
    time.sleep(1)

    response = requests.get(url)

    while response.status_code / 100 > 2:
        log_warning("Something wrong with '%s' (response code: %d)" % (url, response.status_code))

        if response.status_code != 429:  # 429: Too many requests
            return None

        log_warning("Retry GET '%s' after %d seconds." % (url, WAITTING_TIME))
        time.sleep(WAITTING_TIME)

        response = requests.get(url)
        # TODO: Maximum retrying times

    return response.json()


def get_last_line(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            pass
    return line


def time_to_str(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d-%H")


def time_to_day(t):
    return datetime.datetime.fromtimestamp(t).day


def time_to_sec(t):
    return datetime.datetime.fromtimestamp(t).second
