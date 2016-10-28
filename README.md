# BrakeValve Dataflow
[![Build Status](https://travis-ci.org/BrakeValve/dataflow.svg?branch=master)](https://travis-ci.org/BrakeValve/dataflow)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://en.wikipedia.org/wiki/MIT_License)
> Help you think twice and make wise choices on Steam

BrakeValve is a Chrome extension to help Steam buyers making decision on purchasing games. We use novel feature extraction techniques to gain knowledge and insight from the Steam historical data and combined with a robust predictor to achieve over 80% accuracy and F-score.

Click [here](https://brakevalve.github.io/) to see more implementation detail.

## Project Preview

``` markdown
dataflow/
│ 
├── data-crawler/                        
│   ├── historical-price-crawler.py      # Steam price crawler using SteamDB API
│   └── metadata-crawler.py              # Steam metadata crawler using SteamDB API
├── data-preprocessor/                   
│   ├── Game.py                          # Steam Game Object
│   ├── listFile.py                      # file utils
│   └── preprocessor.py                  # preprocessing main function
└─── model/
    └── random-forest-model.py           # training demo using random forest model from `sklearn`
```
## Dependencies

- beautifulsoup4
- requests
