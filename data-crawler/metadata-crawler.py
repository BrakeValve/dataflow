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

parser = OptionParser()
parser.add_option("-o", dest="OUTPUT_DIRECTORY")
(options, args) = parser.parse_args()

if options.OUTPUT_DIRECTORY is not None:
    OUTPUT_DIRECTORY = options.OUTPUT_DIRECTORY

if not os.path.exists(OUTPUT_DIRECTORY):
    print("Can't not find output directory, Create a new one")
    os.makedirs(OUTPUT_DIRECTORY)

ids = [
    u'433950', u'391540', u'237930', u'367580', u'620',
    u'205100', u'322170', u'342560', u'420110', u'13240',
    u'24960', u'400', u'250900', u'341800', u'224820',
    u'231160', u'9420', u'238460', u'373770', u'368340',
    u'213670', u'427520', u'35140', u'242680', u'238320',
    u'219740', u'316720', u'32150', u'413150', u'251370',
    u'107100', u'293780', u'55230', u'319630', u'113200',
    u'102600', u'279800', u'280220', u'370360', u'428550',
    u'360740', u'236090', u'220200', u'221640', u'35720',
    u'13230', u'3590', u'212680', u'70400', u'227000',
    u'431730', u'261570', u'206190', u'206440', u'18500',
    u'264200', u'214560', u'322330', u'48700', u'220',
    u'10', u'219150', u'413410', u'8930', u'266010',
    u'265610', u'204360', u'282070', u'550', u'274190',
    u'236930', u'247080', u'413420', u'218410', u'105600',
    u'207610', u'227300', u'49520', u'324160', u'411960',
    u'284770', u'292030', u'34330', u'339350', u'400910',
    u'250320', u'288160'
]
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
                for j in range(len(rows)/2):
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
