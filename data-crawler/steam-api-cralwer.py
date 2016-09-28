# -*- coding: utf-8 -*-

# TODO: Ignore list
# TODO: If we got 429 error, wait some time then re-try

from argparse import ArgumentParser
import os
import requests
import sys
import json
import time
import datetime

# === Constants ===
APP_LIST_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
APP_URL_PREFIX = "http://store.steampowered.com/api/appdetails?appids="
APP_ATTRS = [
    # "type",
    "name",
    "steam_appid",
    "required_age",
    "is_free",
    "controller_support",
    "dlc",
    # "detailed_description",
    # "about_the_game",
    "short_description",
    "supported_languages",
    # "header_image",
    # "website",
    # "pc_requirements",
    # "mac_requirements",
    # "linux_requirements",
    # "legal_notice",
    "developers",
    "publishers",
    # "price_overview",
    "packages",
    "package_groups",
    "platforms",
    "categories",
    "genres",
    # "screenshots",
    # "movies",
    "recommendations",
    # "achievements",
    "release_date",
    "support_info",
    # "background"
]
TARGET_COUNTRY = ["us", "br", "ca", "eu", "kr", "mx", "nz", "sg", "tr", "uk", "tw"]
START_TIME = time.time()

# === Predefined functions ===


def log_warning(msg):
    print("[WARNING] %s" % msg)


def log_info(msg):
    print("[INFO] %s" % msg)


def log_debug(msg):
    print("[DEBUG] %s" % msg)


def ensure_path(path):
    if not os.path.exists(path):
        print("Can't not find output directory '%s', Create a new one" % path)
        os.makedirs(path)


def retrieve_data(url):
    response = requests.get(url)

    if response.status_code / 100 > 2:
        print("Something wrong with '%s'" % url)
        print("Response code: %d" % response.status_code)
        return None

    return json.loads(response.content)


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


# === Read the argument for the output path ===
parser = ArgumentParser(description="Retrieve the data from offical Steam API")
parser.add_argument("-n", "--num", help="the number of the first apps to be downloaded")
parser.add_argument("-o", "--out", help="the output directory")
parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")
parser.add_argument("-m", "--re-meta", help="re-download exsiting metadata", action="store_true")
args = parser.parse_args()

path = "./data"
if args.out is None:
    log_info("Didn't specify the output path. Use the default one: %s" % path)
else:
    path = args.out

if args.debug:
    log_debug("Debug mode enabled")
if args.re_meta:
    log_info("Redownload all metadata")

# === Ensure the path to the output directories
meta_dir_path = path + "/metadata"
ensure_path(meta_dir_path)
price_dir_path = path + "/price"
ensure_path(price_dir_path)


# === Retrieve the ids of the target applications ===
data = retrieve_data(APP_LIST_URL)
if data is None:
    sys.exit(1)

apps = []
for app in data['applist']['apps']['app']:
    # According to CT's theory, only the apps with id divisible by 10 are games
    if app['appid'] % 10 == 0:
        apps.append((app['appid'], app['name']))

log_info("Found %d applications" % len(apps))

# Debug: We only take the first 10 apps
if args.debug:
    log_debug("Only takes the first 10 apps")
    apps = apps[:10]
elif args.num is not None:
    count = int(args.num)
    log_info("Only takes the first %d apps" % count)
    if count < len(apps):
        apps = apps[:count]

# == Retrieve the metadata ==
for (app_id, app_name) in apps:

    file_path = meta_dir_path + "/app_meta_" + str(app_id) + ".json"

    # Check if the metadata exists
    if (not args.re_meta) and os.path.exists(file_path):
        continue

    # Downloads the json data
    data = retrieve_data(APP_URL_PREFIX + str(app_id))
    if data[str(app_id)]["success"] == False:
        log_warning("Failed to retrieve the data for '%s' (id: %d)" % (app_name, app_id))
        continue
    data = data[str(app_id)]["data"]

    # Only keep the attributes we care about
    new_data = {}
    for attr in APP_ATTRS:
        if attr in data:
            new_data[attr] = data[attr]

    # Save to the file
    with open(file_path, "w") as f:
        f.write(json.dumps(new_data))

# == Retrieve the prices for the target countries ==
for cc in TARGET_COUNTRY:
    cc_dir = price_dir_path + "/" + cc
    ensure_path(cc_dir)

    log_info("Retrieving the price data (country code: %s)" % cc)

    rest_apps = list(apps)
    while len(rest_apps) != 0:

        log_info("There are %d apps left" % len(rest_apps))

        # Retrieve the first 100 apps
        this_time_apps = []
        next_time_apps = []
        for (app_id, app_name) in rest_apps:
            if len(this_time_apps) < 100:
                # Check if we have the price data for this app today
                file_path = cc_dir + "/app_price_" + str(app_id) + ".txt"
                if os.path.exists(file_path):
                    last_line = get_last_line(file_path)
                    time_str = last_line.split(' ')[0]

                    if time_to_day(long(time_str)) == time_to_day(START_TIME):
                        continue

                this_time_apps.append((app_id, app_name))

            else:
                next_time_apps.append((app_id, app_name))
        rest_apps = next_time_apps

        # Retrieve the price of the first 100 apps
        url = APP_URL_PREFIX
        for (app_id, _) in this_time_apps:
            url += str(app_id) + ','
        url = url[:-1] # Remove the last ','
        url += "&cc=" + cc + "&filters=price_overview"
        data = retrieve_data(url)

        # Save the price of the data to the file
        for (app_id, app_name) in this_time_apps:
            if data[str(app_id)]["success"] == False:
                log_warning("Failed to retrieve the price data for '%s' (id: %d)" % (app_name, app_id))
            else:
                # Check if it has price data
                if "price_overview" not in data[str(app_id)]["data"]:
                    log_info("App '%s' (id: %d) is free." % (app_name, app_id))
                    continue

                # Retrieve the price
                price = data[str(app_id)]["data"]["price_overview"]
                init_price = price["initial"]
                final_price = price["final"]

                # Save to the file
                file_path = cc_dir + "/app_price_" + str(app_id) + ".txt"
                with open(file_path, mode='a') as f:
                    f.write("%d %d %d %s\n" % (START_TIME, init_price, final_price, time_to_str(START_TIME)))


# == Finish ==
log_info("Finished. It takes %d seconds totally." % time_to_sec(time.time() - START_TIME))
