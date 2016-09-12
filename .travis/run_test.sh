#!/bin/bash
cd .travis
tar xf test_data.tar.gz
cd ..
python data-preprocessor/preprocessor.py -m .travis/test_meta/ -p .travis/test_price_data/ -t .travis/test_trainging
code=$?
if [ $code -ne 0 ]
then
        echo "Sample training data preprocessing : FAILED"
        exit $code
fi
echo "Sample training data preprocessing : PASSED"
