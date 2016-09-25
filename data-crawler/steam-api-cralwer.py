# -*- coding: utf-8 -*-

# TODO: Skip metadata

from argparse import ArgumentParser
import os
import requests
import sys
import json

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
    # "short_description",
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


# === Predefined functions ===
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


# === Read the argument for the output path ===
parser = ArgumentParser(description="Retrieve the data from offical Steam API")
parser.add_argument("-o", "--out", help="the output directory")
args = parser.parse_args()

path = "./data"
if args.out is None:
    print("Didn't specify the output path. Use the default one: %s" % path)
else:
    path = args.out


# === Ensure the path to the output directories
meta_dir_path = path + "/metadata"
ensure_path(meta_dir_path)

# === Retrieve the ids of the target applications ===
data = retrieve_data(APP_LIST_URL)
if data is None:
    sys.exit(1)

apps = []
for app in data['applist']['apps']['app']:
    # According to CT's theory, only the apps with id divisible by 10 are games
    if app['appid'] % 10 == 0:
        apps.append((app['appid'], app['name']))

print("Found %d applications" % len(apps))

# Debug: We only take the first 10 apps
apps = apps[:10]

# == For each application ==
for (app_id, app_name) in apps:

    # == Retrieve the metadata ==
    data = retrieve_data(APP_URL_PREFIX + str(app_id))
    if data[str(app_id)]["success"] == False:
        print("Failed to retrieve the data for '%s' (id: %d)" % (app_name, app_id))
        continue
    data = data[str(app_id)]["data"]

    # Only keep the attributes we care about
    new_data = {}
    for attr in APP_ATTRS:
        if attr in data:
            new_data[attr] = data[attr]

    # Save to the file
    with open(meta_dir_path + "/app_meta_" + str(app_id) + ".json", "w") as f:
        f.write(json.dumps(new_data))

    # TODO: Retrieve the prices for the target countries
