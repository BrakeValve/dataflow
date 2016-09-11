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


def out_append(o, t, price, o_price):
    o.append(' '.join(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d"), str(t), str(price), str(o_price)) + '\n')

OUTPUT_DIRECTORY = '../../new_price_data'

parser = OptionParser()
parser.add_option("-o", dest="OUTPUT_DIRECTORY")
(options, args) = parser.parse_args()

if options.OUTPUT_DIRECTORY is not None:
    OUTPUT_DIRECTORY = options.OUTPUT_DIRECTORY

if not os.path.exists(OUTPUT_DIRECTORY):
    print "Can't not find output directory, Create a new one"
    os.makedirs(OUTPUT_DIRECTORY)

ids = [
    '10', '102600', '105600', '107100', '113200',
    '13230', '13240', '18500', '204360', '205100',
    '206190', '206440', '207610', '212680', '213670',
    '214560', '218410', '219150', '219740', '220',
    '220200', '221640', '224820', '227000', '227300',
    '231160', '236090', '236930', '237930', '238320',
    '238460', '242680', '247080', '24960', '250320',
    '250900', '251370', '261570', '264200', '265610',
    '266010', '274190', '279800', '280220', '282070',
    '284770', '288160', '292030', '293780', '316720',
    '319630', '32150', '322170', '322330', '324160',
    '339350', '341800', '342560', '34330', '35140',
    '35720', '3590', '360740', '367580', '368340',
    '370360', '373770', '391540', '400', '400910',
    '411960', '413150', '413410', '413420', '420110',
    '427520', '428550', '431730', '433950', '48700',
    '49520', '550', '55230', '620', '70400',
    '8930', '9420'
]

ids = ['620']

country = ['us', 'br', 'ca', 'eu', 'kr', 'mx', 'nz', 'sg', 'tr', 'uk']
country = ['us']
for c in country:
    if not os.path.exists(OUTPUT_DIRECTORY+'/'+c):
        os.makedirs(OUTPUT_DIRECTORY+'/'+c)

for cc in country:
    for appid in ids:

        print 'Parse APP No.  '+appid+' '+cc
        # Random sleep for a few seconds to simulate human query
        # time.sleep(randint(1,5))
        response = requests.get("https://steamdb.info/api/GetPriceHistory/?appid=" + appid + "&cc=" + cc)
        if response.status_code == 200:
            cont = json.loads(response.content)
            if cont['success'] is True:
                result = cont['data']['final']
                init = cont['data']['initial']
                out = []
                l = len(result)
                if l > 0:
                    last = ''
                    f_name = OUTPUT_DIRECTORY+'/'+cc+'/new_app_'+cc+'_'+appid+'.txt'
                    if os.path.isfile(f_name):
                        # if previous data is exist, read through the file to find the last data point
                        with open(f_name, 'r') as f:
                            for line in f:
                                pass
                            last = line
                        # Append the new data point
                    with open(f_name, 'a+') as f:
                        if last == '':
                            lastline = []
                            lastline.extend(result[0])
                            lastline.append(init[0][1])
                            out_append(out, int(lastline[0]/1000), lastline[1], lastline[2])
                        else:
                            lastline = last.split()

                        lastTime = int(lastline[0]/1000)

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
                            nowTime = time.time()
                            while edTime < nowTime:
                                out_append(out, edTime, ed[1], ed_init[1])
                                edTime = edTime + 86400
                            out_append(out, nowTime, ed[1], ed_init[1])
                        else:
                            nowTime = time.time()
                            lastTime = lastTime + 86400
                            while lastTime < nowTime:
                                out_append(out, lastTime, lastline[1], lastline[2])
                                lastTime = lastTime + 86400
                            out_append(out, nowTime, lastline[1], lastline[2])

                        f.write(''.join(out))
