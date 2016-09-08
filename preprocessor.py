# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 16:16:41 2016

@author: SISQUAKE
"""
from optparse import OptionParser

def main():
    
    parser = OptionParser();
    parser.add_option("-m",dest = "METADATA_DIRECTORY");
    parser.add_option("-p",dest="PRICE_DATA_DIRECTORY");
    parser.add_option("-t",dest="TRAINING_OUTPUT_DIRECTORY");
    (options, args) = parser.parse_args();
    
    #print options.METADATA_DIRECTORY;
    #print parser.PRICE_DATA_DIRECTORY;
    #print parser.OUTPUT_TRAINING;
    
    
    
if __name__ == "__main__":
    main();