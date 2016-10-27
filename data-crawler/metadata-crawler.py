# -*- coding: utf-8 -*-
"""
Created on Thu Sep 09 10:16:41 2016

@author: SISQUAKE
"""

import requests
import json
from bs4 import BeautifulSoup
from optparse import OptionParser
import os

OUTPUT_DIRECTORY = '../../new_meta'


def pruned_list(original_list):
    return list(filter(lambda x: x.strip() != '', original_list))


def load_list(url):
    response = requests.get(url)
    return pruned_list(response.text.split('\n'))


def load_ids():
    return load_list('https://raw.githubusercontent.com/BrakeValve/data/apps/apps')

parser = OptionParser()
parser.add_option("-o", dest="OUTPUT_DIRECTORY")
(options, args) = parser.parse_args()

if options.OUTPUT_DIRECTORY is not None:
    OUTPUT_DIRECTORY = options.OUTPUT_DIRECTORY

if not os.path.exists(OUTPUT_DIRECTORY):
    print("Can't not find output directory, Create a new one")
    os.makedirs(OUTPUT_DIRECTORY)

ids = load_ids()

itr = 0
attrs = ['App ID', 'App Type', 'Name', 'Developer', 'Publisher', 'Release Date']


for appid in ids:

    response = requests.get("https://steamdb.info/app/" + appid + "/")

    if response.status_code == 200 and not os.path.exists(OUTPUT_DIRECTORY + '/app_meta_' + appid + '.json'):
        app_dict = {}

        soup = BeautifulSoup(response.content, "html.parser")
        meta = soup.find_all(class_='row app-row')
        table = BeautifulSoup(str(meta), "html.parser")
        rows = table.find_all('td')
        if(rows[3].string != 'Downloadable Content'):
            print("Parse APP: " + appid + " No " + str(itr))
            for a in attrs:
                for j in range(int(len(rows)/2)):
                    attr = str(rows[2*j]).replace(">", "#").replace("<", "#").split("#")[2]

                    if attr == a:
                        if (attr == 'Developer') | (attr == 'Publisher'):
                            val = str(rows[2*j+1]).replace(">", "#").replace("<", "#").split("#")[4]
                        else:
                            val = str(rows[2*j+1]).replace(">", "#").replace("<", "#").split("#")[2]

                        app_dict[attr] = val
                        break

            info = BeautifulSoup(str(soup.find_all(id='info')), "html.parser")
            rows = info.find_all('td')

            app_dict['metacritic_score'] = -1
            app_dict['dlc'] = 0

            # Genres
            l = len(rows)
            for i in range(0, l, 2):
                if rows[i].string == 'Genres':
                    app_dict['Genres'] = rows[i+1].string

                elif rows[i].string == 'metacritic_score':
                    app_dict['metacritic_score'] = rows[i+1].string
                    dlc = BeautifulSoup(str(soup.find_all(href='/app/'+appid+'/dlc/')), "html.parser")
                    dlc_rows = dlc.find_all('span')
                    if len(dlc_rows) > 0:
                        # dlc count
                        app_dict['dlc'] = int(dlc_rows[1].string)

            with open(OUTPUT_DIRECTORY+'/app_meta_'+appid+'.json', 'w') as f:
                f.write(''.join(json.dumps(app_dict, ensure_ascii=False)))

            itr = itr + 1

        else:
            print("Error on No: " + str(itr))
            itr = itr + 1
