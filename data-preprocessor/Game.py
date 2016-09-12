# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 21:25:11 2016

@author: SISQUAKE
"""
import json
import datetime
import math


def mean_var(seq):
    if(len(seq) == 0):
        return [0, 0]
    m = sum(seq)/len(seq)
    v = sum(map(lambda x: (x-m)*(x-m), seq))/len(seq)
    return [m, v]


class Game:
    # some CCC curve parameter
    MIN_WAIT_DAY = 20
    THRESHOLD = 0.2

    def __init__(self, json_path_string, target_country):
        try:
            f = open(json_path_string, 'r')
        except IOError:
            print('Cannot open file', json_path_string)
        else:
            # parse json
            tmp_json = json.loads(f.read())

            # set target country
            self.target_country = target_country

            # Binary feature
            self.id = tmp_json["App ID"]
            self.developer = tmp_json["Developer"]

            if tmp_json.get("Publisher") is None:
                self.publisher = self.developer
            else:
                self.publisher = tmp_json["Publisher"]

            if tmp_json.get("Genres") is None:
                self.geners = []
            else:
                self.geners = tmp_json['Genres'].split(',')

            # pares to datetime
            if tmp_json.get("Release Date") is None:
                self.release_date = datetime.datetime.now() - datetime.timedelta(days=730)
            else:
                self.release_date = datetime.datetime.strptime(
                    tmp_json["Release Date"].replace(' 0', ' '), '%B %d, %Y '
                )

            self.test_begin = 0

            self.days_from_release = 0

            # Country hash map
            self.country_set = {}

            # Label of each time slot
            self.lables = []

    class Country:
        def __init__(self, name):
            self.name = name

            # Static feature
            self.mean_duration = 0.0
            self.var_duration = 0.0
            self.mean_discount = 0.0
            self.var_discount = 0.0
            self.mean_price = 0.0
            self.var_price = 0.0
            self.mean_org_price = 0.0
            self.var_org_price = 0.0

            # Data Array

            self.prices = []
            self.org_prices = []
            self.trimmed_discounts = []
            self.discounts = []
            self.durations = []

            self.times = []
            self.days_since_last_dis = []

        def extractTimeUniFeature(self):

            # Every day price
            [self.mean_price, self.var_price] = mean_var(self.prices)

            # Every day origin price (msrp may decriese )
            [self.mean_org_price, self.var_org_price] = mean_var(self.org_prices)

            # discount to every day
            [self.mean_discount, self.var_discount] = mean_var(self.trimmed_discounts)

            # Druation of every discount
            [self.mean_duration, self.var_duration] = mean_var(self.durations)

        def extractTimeRelFeature(self):

            # Compute the delta between each time slot to its lastest discount
            isCountinue = False
            count = 1
            for dis in self.discounts:
                if dis != 1.0 and not isCountinue:
                    self.days_since_last_dis.append(0)
                elif dis != 1.0 and isCountinue:
                    isCountinue = False
                    self.days_since_last_dis.append(0)
                    count = 1
                elif dis == 1.0 and not isCountinue:
                    isCountinue = True
                    self.days_since_last_dis.append(count)
                    count = count + 1
                elif dis == 1.0 and isCountinue:
                    self.days_since_last_dis.append(count)
                    count = count + 1

    # add a country historical data and compute its statistics
    def addcountry(self, name, file_path_string):
        try:
            f = open(file_path_string, 'r')
        except IOError:
            print('Cannot open file', file_path_string)
        else:
            c = self.Country(name)

            self.country_set[name] = c

            pre_time = ""
            for line in f:
                [timestamp, p, o_p] = map(float, line.split())
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                # Prevent duplicate time slots
                if timestamp != pre_time:
                    c.times.append(timestamp)
                    c.prices.append(p)
                    c.org_prices.append(o_p)
                    if p == 0:
                        c.discounts.append(0.0)
                    else:
                        c.discounts.append(p / o_p)
                    pre_time = timestamp
            f.close()

            if len(c.prices) > 0:
                # Caulacte durations of evey discoint, and the price of every discounts
                pre = 1.0
                flag = False
                count = 0
                for dis in c.discounts:
                    if dis == 1 and not flag:
                        flag = True
                    elif dis == 1 and flag:
                        count = count + 1
                    elif dis < 1 and flag:
                        flag = False
                        c.durations.append(count)
                        count = 0
                    if dis < pre:
                        c.trimmed_discounts.append(dis)
                    pre = dis
                if flag:
                    c.durations.append(count)

                # Feature extraction:

                # Extract Time Uniform featrue : compute statistics data array

                c.extractTimeUniFeature()

    def cleanDataAndEctractTime(self):
        # Data Cleaning

        for c in self.country_set.values():
            if c.name != self.target_country:
                self.fillMissingValue(c)
            else:
                # compute delta between the first date and the release date
                self.days_from_release = int(
                    (datetime.datetime.strptime(c.times[len(c.times)-1], '%Y-%m-%d') - self.release_date).days
                )

            # Exract Time Releative Feature on each time slot
            c.extractTimeRelFeature()

    def fillMissingValue(self, c):

        # Filling head missing values
        dis = c.discounts[0]

        c_first_date = c.times[0]
        pre_discounts = []
        for t in self.country_set[self.target_country].times:
            if c_first_date == t:
                break
        # print c_first_date +' '+t
            pre_discounts.append(dis)

        pre_discounts.extend(c.discounts)
        # print 'pre :' + str(len(pre_discounts));
        c.discounts = pre_discounts

        # Filling tail missing values

        dis = c.discounts[len(c.prices) - 1]
        # shift one day
        c_last_date = (
            datetime.datetime.strptime(c.times[len(c.times)-1], '%Y-%m-%d') + datetime.timedelta(days=1)
        ).strftime('%Y-%m-%d')
        # c_last_date = c.times[len(c.times)-1];
        flag = False
        for t in self.country_set[self.target_country].times:

            if c_last_date == t:
                flag = True
            if flag:
                c.discounts.append(dis)

    def setTestStartPoint(self, TRAINING_RATE):
        target_c = self.country_set.get(self.target_country)
        if(self.days_from_release >= 0):
            self.test_begin = int(math.floor(len(target_c.times) * TRAINING_RATE))
        else:
            self.test_begin = math.floor((len(target_c.times) + self.days_from_release) * TRAINING_RATE)
            self.test_begin = int(self.test_begin - self.days_from_release)

    def getLabels(self):

        # Use CCC curve to genrative reasonable labels
        # Note that CCC curve will highly affect the traing result

        target_c = self.country_set.get(self.target_country)
        durations = target_c.durations
        count = 1
        flag = False
        index = 0

        for dis in target_c.discounts:
            if dis != 1.0 and not flag:
                # if it had discount, label it Don't buy
                self.lables.append(1)
            elif dis != 1.0 and flag:
                flag = False
                self.lables.append(1)
                count = 1
                index = index + 1
            elif dis == 1.0 and not flag:
                flag = True
                # if it haven't had discount for more than 20 days, apply CCC curve
                if durations[index] <= 20 or count + 20 >= durations[index]:
                    self.lables.append(0)
                else:
                    self.lables.append(math.log(float((durations[index]-20)) / count) / math.log(durations[index]))
                count = count + 1
            elif dis == 1.0 and flag:

                if durations[index] <= 20 or count + 20 >= durations[index]:
                    self.lables.append(0)
                else:
                    self.lables.append(math.log(float((durations[index]-20)) / count) / math.log(durations[index]))
                count = count + 1
