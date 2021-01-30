#!/bin/bash

# Script wraps over the main python script. Crontab runs this script
cd $(dirname $0)
source venv/bin/activate
./detect_ip_change.py >> tmp/detect_ip.log
deactivate
cd -
