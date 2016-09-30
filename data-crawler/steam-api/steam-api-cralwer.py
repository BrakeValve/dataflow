# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import os
import sys
import json
import time

from util import log_info, log_warning, log_debug, ensure_path, retrieve_data
from util import get_last_line, time_to_str, time_to_day, time_to_sec
from util import APP_LIST_URL, APP_URL_PREFIX, APPS_PER_REQUEST

# === Constants ===
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


def read_ignore_list(path):
    apps = []

    if not os.path.exists(path):
        log_warning("Can't not find the ignore list at '%s'" % path)
        return apps

    with open(path, 'r') as f:
        for line in f:
            app_id = line.split(' ')[0]
            apps.append(int(app_id))

    return apps


# === Read the argument for the output path ===
parser = ArgumentParser(description="Retrieve the data from offical Steam API")
parser.add_argument("-n", "--num", help="the number of the first apps to be downloaded")
parser.add_argument("-o", "--out", help="the output directory")
parser.add_argument("-d", "--debug", help="enable debug mode", action="store_true")
parser.add_argument("-m", "--re-meta", help="re-download exsiting metadata", action="store_true")
args = parser.parse_args()

path = "./data"
ignore_file = "./ignore_apps.txt"
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

# Remove the ignored applications
ignores = read_ignore_list(ignore_file)
new_list = []
for (app_id, app_name) in apps:
    if app_id in ignores:
        if args.debug:
            log_debug("Ignore %s (id: %d)" % (app_name, app_id))
        continue

    new_list.append((app_id, app_name))
log_info("There are %d apps ignored" % (len(apps) - len(new_list)))
apps = new_list


# == Retrieve the metadata ==
count = 0
down_count = 0
for (app_id, app_name) in apps:
    count += 1

    file_path = meta_dir_path + "/app_meta_" + str(app_id) + ".json"

    # Check if the metadata exists
    if (not args.re_meta) and os.path.exists(file_path):
        continue

    # Downloads the json data
    data = retrieve_data(APP_URL_PREFIX + str(app_id) + "&cc=us")
    if data is None:
        continue

    if data[str(app_id)]["success"] is False:
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

    down_count += 1
    if down_count % 10 == 0:
        log_info("%d applications' metadata remained to be checked" % (len(apps) - count))


# == Retrieve the prices for the target countries ==
for cc in TARGET_COUNTRY:
    cc_dir = price_dir_path + "/" + cc
    ensure_path(cc_dir)

    log_info("Retrieving the price data (country code: %s)" % cc)

    rest_apps = list(apps)
    while len(rest_apps) != 0:

        log_info("There are %d apps left" % len(rest_apps))

        # Retrieve the first {APPS_PER_REQUEST} apps
        this_time_apps = []
        next_time_apps = []
        for (app_id, app_name) in rest_apps:
            if len(this_time_apps) < APPS_PER_REQUEST:
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
        url = url[:-1]  # Remove the last ','
        url += "&cc=" + cc + "&filters=price_overview"
        data = retrieve_data(url)
        if data is None:
            continue

        # Save the price of the data to the file
        for (app_id, app_name) in this_time_apps:
            if data[str(app_id)]["success"] is False:
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
