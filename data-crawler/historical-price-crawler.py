# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 22:35:21 2016

@author: SISQUAKE
"""

import requests
import json
import time
from optparse import OptionParser
import datetime
import os


def days(t):
    return datetime.datetime.fromtimestamp(t).day


def out_append(o, t, price, o_price):
    t = int(t)
    string = ' '.join([str(t),  str(price), str(o_price), datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d-%H")])
    o.append(string + '\n')


def pruned_list(original_list):
    return list(filter(lambda x: x != '', map(lambda x: x.strip(), original_list)))


def load_list(url):
    response = requests.get(url)
    return pruned_list(response.text.split('\n'))


def load_ids():
    return load_list('https://raw.githubusercontent.com/BrakeValve/data/apps/apps')


def load_regions():
    return load_list('https://raw.githubusercontent.com/BrakeValve/data/apps/regions')


OUTPUT_DIRECTORY = '../../price_data'

parser = OptionParser()
parser.add_option("-o", dest="OUTPUT_DIRECTORY")
(options, args) = parser.parse_args()

if options.OUTPUT_DIRECTORY is not None:
    OUTPUT_DIRECTORY = options.OUTPUT_DIRECTORY

if not os.path.exists(OUTPUT_DIRECTORY):
    print("Can't not find output directory, Create a new one")
    os.makedirs(OUTPUT_DIRECTORY)


ids = load_ids()
country = load_regions()

for c in country:
    if not os.path.exists(OUTPUT_DIRECTORY+'/'+c):
        os.makedirs(OUTPUT_DIRECTORY+'/'+c)

for cc in country:
    for appid in ids:

        print('Parse APP No.  ' + appid + ' ' + cc)
        # Random sleep for a few seconds to simulate human query
        # time.sleep(randint(1,5))

        nowTime = time.time()

        f_name = OUTPUT_DIRECTORY+'/'+cc+'/new_app_'+cc+'_'+appid+'.txt'
        last = ''
        if os.path.isfile(f_name):
            # if previous data is exist, read through the file to find the last data point
            with open(f_name, 'r') as f:
                for line in f:
                    pass
                last = line
            lastline = last.split()
            lastTimeOfFile = int(lastline[0])
            if(days(lastTimeOfFile) == days(nowTime)):

                print(appid + ' ' + cc + ' is already up to date.')
                continue

        response = requests.get("https://steamdb.info/api/GetPriceHistory/?appid=" + appid + "&cc=" + cc)
        if response.status_code == 200:
            print('Crawler requert success!')
            cont = json.loads(response.text)
            if cont['success'] is True:
                result = cont['data']['final']
                init = cont['data']['initial']
                out = []
                l = len(result)
                if l > 0:
                    with open(f_name, 'a+') as f:
                        # Append the new data point
                        if last == '':
                            lastline = []
                            lastline.extend(result[0])
                            lastline.append(init[0][1])
                            lastTime = int(lastline[0])/1000
                            out_append(out, int(lastline[0]/1000), lastline[1], lastline[2])
                        else:
                            lastline = last.split()
                            lastTime = int(lastline[0])

                        for ptr in range(l):
                            if result[ptr][0]/1000 > lastTime:
                                break

                        if(ptr != l - 1):
                            ftTime = result[ptr][0]/1000
                            lastTime = lastTime + 86400
                            while lastTime < ftTime:
                                out_append(out, lastTime, lastline[1], lastline[2])
                                lastTime = lastTime + 86400
                            for i in range(ptr, l-1):
                                st = result[i]
                                st_init = init[i]
                                stTime = st[0] / 1000
                                ed = result[i+1]
                                edTime = ed[0] / 1000
                                while stTime < edTime:
                                    out_append(out, stTime, st[1], st_init[1])
                                    stTime = stTime + 86400
                            ed = result[l - 1]
                            ed_init = init[l - 1]
                            edTime = ed[0] / 1000

                            while edTime < nowTime:
                                out_append(out, edTime, ed[1], ed_init[1])
                                edTime = edTime + 86400
                            if(days(edTime - 86400) != days(nowTime)):
                                out_append(out, nowTime, ed[1], ed_init[1])
                        else:
                            nowTime = time.time()
                            lastTime = lastTime + 86400
                            while lastTime < nowTime:
                                out_append(out, lastTime, lastline[1], lastline[2])
                                lastTime = lastTime + 86400
                            if(days(lastTime - 86400) != days(nowTime)):
                                out_append(out, nowTime, lastline[1], lastline[2])

                        f.write(''.join(out))
        else:
            print('Something wrong! Status code : ' + str(response.status_code))
