# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys
import codecs

from util import retrieve_data, log_info
from util import APP_LIST_URL, APP_URL_PREFIX


# === Read the argument for the output path ===
parser = ArgumentParser(description="Generates a list for the apps that cannot be found from Steam API")
parser.add_argument("-o", "--out", help="the output path")
args = parser.parse_args()

ignore_file = "./ignore_apps.txt"
if args.out is None:
    log_info("Didn't specify the output path. Use the default one: %s" % ignore_file)
else:
    ignore_file = args.out


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


# === Opens the ingore file ===
ignore_file = codecs.open(ignore_file, 'w', "utf-8")


# === Try to read the price data of apps ===
while len(apps) != 0:

    log_info("There are %d apps left for check" % len(apps))

    # Retrieve the first 100 apps
    this_time_apps = []
    next_time_apps = []
    for (app_id, app_name) in apps:
        if len(this_time_apps) < 250:
            this_time_apps.append((app_id, app_name))
        else:
            next_time_apps.append((app_id, app_name))
    apps = next_time_apps

    # Retrieve the price of the first 100 apps
    url = APP_URL_PREFIX
    for (app_id, _) in this_time_apps:
        url += str(app_id) + ','
    url = url[:-1]  # Remove the last ','
    url += "&cc=us&filters=price_overview"
    data = retrieve_data(url)
    if data is None:
        continue

    # Save the price of the data to the file
    for (app_id, app_name) in this_time_apps:
        if data[str(app_id)]["success"] is False:
            log_info("Add '%s' (id: %d) to the ignore list" % (app_name, app_id))
            ignore_file.write("%d  # %s\n" % (app_id, app_name))


ignore_file.close()
