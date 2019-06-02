# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import base64
import json
import sys
import subprocess

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

def unpadded_b64decode(b64str):
    paddedstr = b64str + '=' * (-len(b64str) % 4)
    return base64.urlsafe_b64decode(paddedstr)
    
def decode_url_rss(url):
    config_fields = ["server", "server_port", "protocol", "method", "obfs", "password"]

    parsed_result = urlparse(url)
    ssconfig = unpadded_b64decode(parsed_result.netloc)

    config, param = ssconfig.split('/')
    config = dict(zip(config_fields, config.split(':')))
    config['password'] = unpadded_b64decode(config['password'])

    param = parse_qs(param)
    param = {k: unpadded_b64decode(v[0]) for k, v in param.items()}

    # fornow, we ignore the params
    print(param)
    return config

def latency_test(host):
    p = subprocess.Popen(["ping", '-c', '6', host], stdout = subprocess.PIPE)
    print('finish', host)
    stat = p.communicate()[0].split('\n')[-2]
    tags = stat.split()[-4].split('/')
    numbers = map(float, stat.split()[-2].split('/'))
    return host, dict(zip(tags, numbers))

parser = argparse.ArgumentParser(description='Convert base64 shadowsocks RSS stream into JSON files')
parser.add_argument('-o', '--output_file', type=str, help='Output JSON filename, use stdin default')
parser.add_argument('-i', '--input_file', type=str, help='Input base64 filename, use stdout default')

args = parser.parse_args()

infile = sys.stdin
if args.input_file:
    pass

indata = infile.read()

# filter out the first line
configs = map(decode_url_rss, base64.urlsafe_b64decode(indata).split()[1:])

# filter out the servers
allowed_locations = [
    # China, 
    # '\xe4\xb8\xad\xe5\x9b\xbd',
    # USA
    # '\xe7\xbe\x8e\xe5\x9b\xbd',
    # Hongkong
    '\xe9\xa6\x99\xe6\xb8\xaf',
    # Singapoo
    '\xe6\x96\xb0\xe5\x8a\xa0\xe5\x9d\xa1',
    # Japan
    '\xe6\x97\xa5\xe6\x9c\xac'
]

filtered_configs = filter(lambda c: any(map(lambda loc: loc in c['param']['comment'], allowed_locations)), configs)

# get latency
latency = dict(map(lambda c: latency_test(c['server']), filtered_configs))

# get the neareast server
filtered_configs = sorted(filtered_configs, key=lambda k: latency[k['server']]['avg']) 



print(latency)
print(filtered_configs[0], filtered_configs[0]['server'] )


