#! /usr/bin/env python 
# coding: utf-8


import json
import re


data = []
d1 = {}

pattern_mounts = re.compile(r'(?!.*(autofs|usbfs).*)[0-9/].*? (?P<FSNAME>/.*?) (?P<FSTYPE>.*?) .*')

with open('/proc/mounts', 'rb') as f:
    for line in f:
        m = pattern_mounts.search(line)
        if m:
           d = m.groupdict()
           d1['{#FSNAME}'] = d['FSNAME']
           d1['{#FSTYPE}'] = d['FSTYPE']
           data.append(d1)

discovery = { "data":data }


encodedjson = json.dumps(discovery, sort_keys=True, indent=4, separators=(',', ':'))

print encodedjson
