#!/usr/bin/python

import sys, urllib.parse, json
from optparse import OptionParser

from resources.lib.onesoccer import *

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
    layout = onesoccer.getLayout()
    for c in layout:
        print('"{}": "{}"'.format(c['id'], c['title']['en']))
elif options.category:
    layout = onesoccer.getLayout()

    for c in layout:
        if c['id'] == options.category:
            category = c
            break
    if category == None:
        print('Unable to find category "{}"'.format(options.category))
        sys.exit(1)
    for d in category['data']:
        print('"{}": "{}" ({})'.format(d['id'] if d['live'] else d['mongoId'], d['title'], d['live']))
        print(d)

    sys.exit(0)
elif options.stream:
    stream = onesoccer.getManifest(options.stream, options.live)
    print('Stream is "{}"'.format(stream))
    sys.exit(0)
else:
    parser.print_help()
    sys.exit(0)
