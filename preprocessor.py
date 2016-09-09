# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 16:16:41 2016

@author: SISQUAKE
"""
from optparse import OptionParser
import os

def listFilePath(path):
    file_path = [];
    file_name = [];
    for (dirpath, dirnames, filenames) in os.walk(path):
        for name in filenames:
            tmp = os.path.join(dirpath, name);
            file_path.append(tmp);
            file_name.append(name);
        break

    return {'file_path':file_path,'file_name':file_name}

#def main():
    
parser = OptionParser();
parser.add_option("-m",dest = "METADATA_DIRECTORY");
parser.add_option("-p",dest="PRICE_DATA_DIRECTORY");
parser.add_option("-t",dest="TRAINING_OUTPUT_DIRECTORY");
(options, args) = parser.parse_args();

#print options.METADATA_DIRECTORY;
#print parser.PRICE_DATA_DIRECTORY;
#print parser.OUTPUT_TRAINING;

# Store for Binary feature needs
 
developer_set = {};
publisher_set = {};
genres_set = {};

# Store ID to Game Object

list_meta = listFilePath('../new_meta');

for meta_path in list_meta['file_path']:
    
        
    
#if __name__ == "__main__":
#    main();

