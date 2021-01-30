#!/usr/bin/env python3

import smtplib, requests, json
from pathlib import Path
from secrets import *

# Open ip.current file and read old ip
TEMP_FOLDER = Path('tmp')
if not TEMP_FOLDER.exists():
    TEMP_FOLDER.mkdir()

LAST_IP_FILE = TEMP_FOLDER.joinpath('ip.current')
if not LAST_IP_FILE.exists():
    LAST_IP_FILE.touch()

old_ip = LAST_IP_FILE.read_text()


# Do a api request to get current ip
IP_URL = 'https://api64.ipify.org'

current_ip = requests.get(IP_URL)

if current_ip:
    current_ip = current_ip.content.decode('utf-8')


# If both are different, need to perform multiple actions
if current_ip != old_ip:

    # Send mail from waspberry's mail to main mail account
    message = """From: waspberry@saikat.app\nTo: saikat626@gmail.com\nSubject: IP change notification

    Ip changed from %s to %s
    """ %(old_ip, current_ip)

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, GMAIL, message)
        server.quit()
    except smtplib.SMTPException as e:
        print('SMTPException: %s', e)

    # Update gandi's dns
    existing_dns_req = requests.get(GANDI_DNS_RECORD_URL, headers={'Authorization': GANDI_API_KEY})
    if existing_dns_req:
        existing_dns = json.loads(existing_dns_req.content)

        # find entry with A records and modify it
        for entry in existing_dns:
            if 'rrset_type' in entry and entry['rrset_type'] == 'A':
                entry['rrset_values'] = [f'{current_ip}']
            del entry['rrset_href']

        # Sync changes
        update_dns_req = requests.put(GANDI_DNS_RECORD_URL, headers={'Authorization': GANDI_API_KEY,
                'Content-Type': 'application/json'}, data=json.dumps({'items': existing_dns}))
        if update_dns_req.status_code != 201:
            print('ERROR: Unable to update dns')


    # Update current ip file
    with open(LAST_IP_FILE, 'w') as ip_file:
        ip_file.write(current_ip)
