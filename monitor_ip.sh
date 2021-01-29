#!/bin/bash

# Script wraps over the main python script. Crontab runs this script
source venv/bin/activate
./detect_ip_change.py >> tmp/detect_ip.log
deactivate
