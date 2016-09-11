#!/bin/bash
cd .travis
tar xf test_data.tar.gz
cd ..
python data-preprocessor/preprocessor.py -m .travis/test_meta/ -p .travis/test_price_data/ -t .travis/test_trainging
echo "Sample training data preprocessing : PASSED"
