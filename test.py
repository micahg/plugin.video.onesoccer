#!/usr/bin/env python3
import sys, urllib.parse, json
from optparse import OptionParser

from resources.lib.onesoccer import *

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# parse the options
parser = OptionParser()
parser.add_option('-u', '--user', type='string', dest='user',
                  help="Username for authentication")
parser.add_option('-p', '--password', type='string', dest='password',
                  help="Password for authentication")
parser.add_option('-l', '--layout', action='store_true', dest='layout',
                  help="Show Categories")
parser.add_option('-c', '--category', type='string', dest='category',
                  help="Show Category items")
parser.add_option('-s', '--stream', type='string', dest='stream',
                  help="Get stream address")
parser.add_option('-L', '--live', action='store_true', dest='live',
                  help="Stream is live or not")
(options, args) = parser.parse_args()

onesoccer = OneSoccer()

if options.user and options.password:
    if not onesoccer.login(options.user, options.password):
        sys.exit(1)
    sys.exit(0)
elif options.layout:
    layout = onesoccer.get_layout()
    for item in layout:
        print('"{}": "{}"'.format(item['id'], item['label']['en']))
elif options.category:
    layout = onesoccer.get_layout()
    for item in layout:
        if item['id'] == options.category:
            category = item
            break
    if category == None:
        print('Unable to find category "{}"'.format(options.category))
        sys.exit(1)
    for d in category['data']:
        thing = onesoccer.simplifyDatum(d)
        print(thing)

    sys.exit(0)
elif options.stream:
    datum = None
    layout = onesoccer.get_layout()
    for item in layout:
        for data in item['data']:
            if data['id'] == options.stream:
                datum = data

    encoded = urllib.parse.urlencode(onesoccer.simplifyDatum(datum))
    decoded = urllib.parse.parse_qs(encoded)
    # decoded = dict((name, value[0]) for name, value in decoded.items())
    stuff = {name:value[0] for (name, value) in decoded.items()}
    print('MICAH DECODED "{}"'.format(stuff))
    print('MICAH DECODED TYPE {}'.format(type(stuff)))
    stream = onesoccer.getManifest(stuff)
    print('Stream is "{}"'.format(stream))
    sys.exit(0)
else:
    parser.print_help()
    sys.exit(0)
