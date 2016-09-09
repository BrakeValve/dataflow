# -*- coding: utf-8 -*-
"""
Created on Thu Sep 09 10:16:41 2016

@author: SISQUAKE
"""

import requests
import json
from bs4 import BeautifulSoup
from optparse import OptionParser

parser = OptionParser();
parser.add_option("-o",dest = "OUTPUT_DIRECTORY");
(options, args) = parser.parse_args();

ids = ['620', u'282070', '264200', '427520', '341800', '400', '424280', u'292030', '374570', '238460', '342560', '433950', '10', u'292030', '413150', '214560', '351640', '420110', '411960', '219150', '250900', '219740', '250320', '220200', '227300', '247080', '213670', '413420', '274190', u'219740', '107100', '102600', '312990', '550', '400910', '231160', '413410', '324160', '206190', '293780', '316720', '205100', '212680', '370360', '407900', u'34330', '265610', '450390', '18500', '32150', '206440', '207610', '220', '105600', '391540', '48700', '367580', '227000', '322170', '70400', '49520', '221640', '319630', '35720', u'8930', '368340', u'237930', '284770', '360740', '13230', '204360', '218410', '13240', '8930', u'204360', '339350', '35140', '251370', '428550', '55230', '242680', u'391540', '322330', '266010', '261570', '236930', u'113200', '373770', '288160', u'227300', '431730', '9420', '238320', '236090', '279800', '224820', '280220', u'24960', '3590', '113200']

itr = 0  
attrs = ['App ID','App Type','Name','Developer','Publisher','Release Date']


for appid in ids :
    
    response = requests.get("https://steamdb.info/app/"+appid+"/")
    
    if response.status_code == 200:
        
        app_dict = {};
        
        soup = BeautifulSoup(response.content)
        meta = soup.find_all(class_='row app-row')
        table = BeautifulSoup(str(meta))
        rows = table.find_all('td')
        if(rows[3].string!='Downloadable Content'):
            
            print 'Parse APP:' + appid + " No " + str(itr)
            for a in attrs:
                for j in range(len(rows)/2):
                    attr = str(rows[2*j]).replace(">","#").replace("<","#").split("#")[2]
                    
                    if attr == a:
                        if (attr == 'Developer') | (attr =='Publisher'):
                            val = str(rows[2*j+1]).replace(">","#").replace("<","#").split("#")[4]
                        else:   
                            val = str(rows[2*j+1]).replace(">","#").replace("<","#").split("#")[2]
                        
                        app_dict[attr] = val;

                        break
            
            info = BeautifulSoup(str(soup.find_all(id = 'info')));
            rows = info.find_all('td')
            
            app_dict['metacritic_score'] = -1;
            app_dict['dlc'] = 0;
            
            # Genres
            l = len(rows);            
            for i in range(0,l,2):
                if rows[i].string == 'Genres' :
                    app_dict['Genres'] = rows[i+1].string;
                    
                elif rows[i].string == 'metacritic_score' :
                    app_dict['metacritic_score'] = rows[i+1].string;
                    dlc = BeautifulSoup(str(soup.find_all(href = '/app/'+appid+'/dlc/')));
                    dlc_rows = dlc.find_all('span')
                    if len(dlc_rows) > 0:
                        # dlc count
                        app_dict['dlc'] = int(dlc_rows[1].string);
                        
            '''
            app_dict[rows[6].string] = rows[7].string;
            
            if(rows[18].string == 'metacritic_score'):
                # metacritic_score
                app_dict[rows[18].string] = rows[19].string;
                                
                dlc = BeautifulSoup(str(soup.find_all(href = '/app/'+appid+'/dlc/')));
                rows = dlc.find_all('span')
                if len(rows) > 0:
                    # dlc count
                    app_dict['dlc'] = rows[1].string;
            
                else:
                     app_dict['dlc'] = 0;
            else:
                app_dict['metacritic_score'] = -1;
                app_dict['dlc'] = 0;
            '''           

            f = open(options.OUTPUT_DIRECTORY+'app_meta_'+appid+'.json','w');
            f.write(''.join(json.dumps(app_dict, ensure_ascii=False) ));
            f.close();
            
            itr = itr + 1;
            
        else:
            print "Error on No :"+str(itr)
            itr = itr + 1;
    
    