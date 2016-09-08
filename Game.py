# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 21:25:11 2016

@author: SISQUAKE
"""
import json
import datetime
import numpy as np

class Game:
    # some CCC curve parameter
    MIN_WAIT_DAY = 20;
    THRESHOLD = 0.2;
    TRAINRATE = 0.8;


    def __init__(self, josn_path_string,target_country):

        try:
            f = open(josn_path_string , 'r')
        except IOError:
            print 'Cannot open file', josn_path_string
        else:    
            # parse json
            tmp_json = json.loads(f.read());
    
            # set target country
            self.target_country = target_country;   
    
            # Binary feature
            self.id = tmp_json["App ID"];
            self.developer = tmp_json["Developer"];
            self.publisher = tmp_json["Publisher"];
            self.geners = tmp_json['Genres'].split(',');
    
            # pares to datetime
            self.release_date = datetime.datetime.strptime(tmp_json["Release Date"].replace(' 0',' '),'%B %d, %Y ');    
            self.days_from_release = 0;
                        
            # Country hash map
            self.country_set = {};
    
            # Label of each time slot
            self.lables = [];

    class Country:
        def __init__(self,name):
            self.name = name;

            # Static feature
            self.mean_duration = 0.0;
            self.var_duration = 0.0;
            self.mean_discount = 0.0;
            self.var_discount = 0.0;
            self.mean_price = 0.0;
            self.var_price = 0.0;
            self.mean_org_price = 0.0;
            self.var_org_price = 0.0;
            
            # Data Array

            self.prices = [];
            self.org_prices = [];
            self.trimmed_discounts = [];
            self.discounts = [];
            self.durations = [];
            
            self.times = [];
            self.days_since_last_dis = [];
            
        def extractTimeUniFeature(self):
            
            # Every day price
            self.mean_price = np.mean(self.prices);
            self.var_price = np.std(self.prices);
            
            # Every day origin price (msrp may decriese ) 
            self.mean_org_price = np.mean(self.org_prices);
            self.var_org_price = np.std(self.mean_org_price);
        
            # discount to every day 
            self.mean_discount = np.mean(self.trimmed_discounts);
            self.var_discount = np.std(self.trimmed_discounts);
            
            # Druation of every discount  
            self.mean_duration = np.mean(self.durations);
            self.var_duration = np.std(self.durations);
            
        def extractTimeRelFeature(self):
            
            #Compute the delta between each time slot to its lastest discount 
            isCountinue = False;
            count = 1;
            for dis in self.discounts:
               if dis != 1.0 and not isCountinue:
                   self.days_since_last_dis.append(0);
               elif dis != 1.0 and isCountinue:
                   isCountinue = False;
                   self.days_since_last_dis.append(0);
                   count = 1;
               elif dis == 1.0 and not isCountinue:
                   isCountinue = True;
                   self.days_since_last_dis.append(count);
                   count = count + 1;
               elif dis == 1.0 and isCountinue:
                   self.days_since_last_dis.append(count);
                   count = count + 1;
               
            
            

    # add a country historical data and compute its statistics
    def addcountry(self,name, file_path_string):
        try:
            f = open(file_path_string , 'r')
        except IOError:
            print 'Cannot open file', file_path_string
        else:
            
            c = self.Country(name);
        
            self.country_set[name]= c;
            
            pre_time = "";
            for line in f:
                [timestamp,p,o_p] = map(float,line.split());
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d");
                # Prevent duplicate time slots
                if timestamp != pre_time:      
                    c.times.append(timestamp);
                    c.prices.append(p);
                    c.org_prices.append(o_p);
                    c.discounts.append(p/o_p);
                    pre_time = timestamp;
            f.close();
            
            if len(c.prices) > 0:        
                
                #Caulacte durations of evey discoint, and the price of every discounts
                pre = 1.0;
                flag = False;
                count = 0;
                for dis in c.discounts:
                    if dis == 1 and not flag:
                        flag = True;
                    elif dis == 1 and flag:
                        count = count + 1;
                    elif dis < 1 and flag:
                        flag = False;
                        c.durations.append(count);
                        count =0;
                    if(dis<pre):
                        c.trimmed_discounts.append(dis);
                    pre = dis;
                if flag:
                    c.durations.append(count);
                    
                # Feature extraction : 
                
                # Extract Time Uniform featrue : compute statistics data array
                    
                c.extractTimeUniFeature();
                
                # Data Cleaning
                
                for c in self.country_set.values:
                    if c.name != self.target_country:
                        self.fillMissingValue(c);
                    else:
                        # compute delta between the first date and the release date
                        self.days_from_release = int((datetime.datetime.strptime(c.times[len(c.times)-1],'%Y-%m-%d') - self.release_date).days);
                
                
                # Exract Time Releative Feature on each time slot
            
                c.extractTimeRelFeature();
        

    def fillMissingValue(self, c):
        
        # Filling head missing values
        
        dis =  c.prices[0]/c.org_prices[0];
        c_first_date = c.times[0];
        pre_discounts = [];
        for t in self.country_set[self.target_country].times:
            if c_first_date == t:
                break;
            pre_discounts.append(dis);
        c.discounts = pre_discounts + c.discounts;
                
        # Filling tail missing values
                
        dis = c.prices[len(c.prices)-1] / c.org_prices[len(c.org_prices)-1];
        # shift one day
        c_last_date = (datetime.datetime.strptime(c.times[len(c.times)-1],'%Y-%m-%d') +datetime.timedelta(days=1)).strftime('%Y-%m-%d');
       
        for t in self.country_set[self.target_country].times:
            if c_last_date == t:
                continue;
            c.discounts.append(dis);

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
