# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 16:16:41 2016

@author: SISQUAKE
"""
from optparse import OptionParser
import os
from Game import Game

def listFilePath(path):
    file_path = [];
    file_name = [];
    directory_path = [];
    for (dirpath, dirnames, filenames) in os.walk(path):
        for name in filenames:
            tmp = os.path.join(dirpath, name);
            file_path.append(tmp);
            file_name.append(name);
        for name in dirnames:
            tmp = os.path.join(dirpath, name);
            directory_path.append(tmp);
        break

    return {'file_path':file_path,'file_name':file_name,'directory_path':directory_path}


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
 
developer_set = {};
publisher_set = {};
genres_set = {};

# Store ID to Game Object

game_set = {};

# Create Game Object form metadata
list_meta = listFilePath(METADATA_DIRECTORY);

for meta_path in list_meta['file_path']:
    g = Game(meta_path,TARGET_COUNTRY);
    game_set[g.id] = g;
   
    
# Add historical data from different conutries

list_c = listFilePath(PRICE_DATA_DIRECTORY);
for c_path in list_c['directory_path']:
    list_price = listFilePath(c_path);
    for price_path in list_price['file_name']:
        filename = price_path.split('_');
        c = filename[2];
        g_id = filename[3].split('.')[0];
        game_set.get(g_id).addcountry(c,c_path+'/'+price_path);
        
        
    


        
        

#if __name__ == "__main__":
#    main();

