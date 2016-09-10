# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 16:16:41 2016

@author: SISQUAKE
"""
from optparse import OptionParser
import os
from Game import Game

def listFilePath(path):
    File = [];
    Dir = [];

    for (dirpath, dirnames, filenames) in os.walk(path):
        for name in filenames:
            tmp = os.path.join(dirpath, name);
            File.append({'path':tmp,'name':name});
        for name in dirnames:
            tmp = os.path.join(dirpath, name);
            Dir.append({'path':tmp,'name':name});
        break

    return {'file' : File , 'dir' : Dir};


#def main():

METADATA_DIRECTORY = '../../new_meta';
PRICE_DATA_DIRECTORY='../../price_data';
TRAINING_OUTPUT_DIRECTORY = '../../traing_data';

TARGET_COUNTRY = 'us';
    
parser = OptionParser();
parser.add_option("-m",dest = "METADATA_DIRECTORY");
parser.add_option("-p",dest="PRICE_DATA_DIRECTORY");
parser.add_option("-t",dest="TRAINING_OUTPUT_DIRECTORY");
(options, args) = parser.parse_args();

if options.METADATA_DIRECTORY != None:
    METADATA_DIRECTORY = options.METADATA_DIRECTORY;
if options.PRICE_DATA_DIRECTORY != None:
    PRICE_DATA_DIRECTORY = options.PRICE_DATA_DIRECTORY;
if options.TRAINING_OUTPUT_DIRECTORY != None:
    TRAINING_OUTPUT_DIRECTORY = options.TRAINING_OUTPUT_DIRECTORY;

# Store for Binary feature needs
 
developer_set = set();
publisher_set = set();
genres_set = set();
country_set = set();

# Store ID to Game Object

game_set = {};

# Create Game Object form metadata
list_meta = listFilePath(METADATA_DIRECTORY);

for meta in list_meta['file']:
    g = Game(meta['path'],TARGET_COUNTRY);
    game_set[g.id] = g;
    
    developer_set.add(g.developer);
    publisher_set.add(g.publisher);
    genres_set = genres_set.union(set(g.geners));
    
    
# Add historical data from different conutries

list_c = listFilePath(PRICE_DATA_DIRECTORY);
for c in list_c['dir']:
    list_price = listFilePath(c['path']);
    for p in list_price['file']:
        country_set.add(c['name']);
        g_id = p['name'].split('_')[3].split('.')[0];
        game_set.get(g_id).addcountry(c['name'],c['path']+'/'+p['path']);
        
        
# Data Cleaning on every country and get lables depend on the target country
for g in game_set.values():
    g.cleanDataAndEctractTime();
    g.getLabels();

# Get AND set of all games' countrysets

for g in game_set.values():
    country_set = country_set & set(g.country_set.keys());

for g in game_set.values():
    
    # filter some bias games    
    if len(g.times) == 0 or g.mean_duration > 250:
        continue;
    target_c = g.country_set[g.target_country];
    
    f = open(TRAINING_OUTPUT_DIRECTORY+'/app_training_'+g.id+'.csv','w');
    
    for i in range (len(g.country_set[g.target_country].times)):
        o = [];
        # fliter preorder price data
        if g.days_from_release + i < 0 :
            continue;
        # Label
        if g.lables[i] > g.THRESHOLD:
            o.append('1');
        else :
            if g.lables[i] > 0 :
                o.append('0');
            else :
                o.append('-1');
        # Developer
        for d in list(developer_set):
            if g.developer == d :
               o.append('1');
            else:
               o.append('0');
        # Publisher
        for p in list(publisher_set):
            if g.publisher == p :
               o.append('1');
            else:
               o.append('0');
        # Genres
        gens = set(g.geners);
        for gen in list(genres_set):
            if gen in gens:
               o.append('1');
            else:
               o.append('0');
        # Static
        #for c in g.country_set
        c = target_c;
        o.extend( [c.mean_duration ,c.var_duration ,c.mean_discount,c.var_discount ,c.mean_price ,c.var_price ,c.mean_org_price ,c.var_org_price]);
        
        # days_since_last_dis
        o.append(target_c.days_since_last_dis[i]);
        for c in g.country_set.values():
            if c.name == target_c.name:
                continue;
            o.append(c.days_since_last_dis[i]);
        # days from release
        o.append(g.days_from_release + i )
        
        # date 
        
    f.close();
    


        
        

#if __name__ == "__main__":
#    main();

