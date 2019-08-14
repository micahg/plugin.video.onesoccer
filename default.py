import xbmc, xbmcplugin, xbmcgui, xbmcaddon, urllib, urlparse, json
#from datetime import datetime
from resources.lib.onesoccer import *
from resources.lib.utils import log

addon_handle = int(sys.argv[1])
getString = xbmcaddon.Addon().getLocalizedString

def authorize(onesoccer):
    username = xbmcaddon.Addon().getSetting("username")
    if len(username) == 0:
        username = None

    password = xbmcaddon.Addon().getSetting("password")
    if len(password) == 0:
        password = None
        username = None

    try:
        onesoccer.login(username, password)
    except OneSoccerAuthError as e:
        log('Authentication error: {}'.format(e.message), True)
        return False

    return True

def createMainMenu(onesoccer):

    layout = onesoccer.getLayout()
    for l in layout:
        labels = {'title': l['name'], 'mediatype': 'video'}
        item = xbmcgui.ListItem(labels['title'])
        item.setInfo('Video', labels)
        encoded_data = urllib.urlencode({'menu': json.dumps(l['data'])})
        path = sys.argv[0] + "?" + encoded_data
        xbmcplugin.addDirectoryItem(addon_handle, path, item, True)
    xbmcplugin.endOfDirectory(addon_handle)
    return None


def getLabels(values):
        title = values['title']
        labels = {'title': title, 'mediatype': 'video'}

        if 'date' in values:
            labels['title'] = u'{} ({})'.format(title, values['date'])

        if 'dt' in values:
            labels['premiered'] = values['dt']

        if 'plot' in values:
            plot = u'{}\n{}'.format(values['plot'], title)
            if 'date' in values:
                plot = u'{}\n{}'.format(plot, values['date'])
            labels['plot'] = plot
            labels['plotoutline'] = plot

        return labels

def createSubMenu(onesoccer, menu):

    gmt = datetime.datetime.utcfromtimestamp(0)
    local = datetime.datetime.fromtimestamp(0)
    delta = local - gmt

    for m in menu:
        values = onesoccer.simplifyDatum(m)

        labels = getLabels(values)
        title = labels['title']

        item = xbmcgui.ListItem(title)
        item.setInfo('Video', labels)
        item.setProperty('IsPlayable', 'true')
        if 'image' in values:
            item.setArt({ 'thumb': values['image'], 'poster': values['image'] })

        path = sys.argv[0] + "?" + urllib.urlencode(values, 'utf-8')
        xbmcplugin.addDirectoryItem(addon_handle, path, item, False)
    xbmcplugin.endOfDirectory(addon_handle)
    return None

def playVideo(onesoccer, data, reauth=False):

    try:
        url = onesoccer.getManifest(data)
    except OneSoccerAuthError as e:
        log(e.message, True)

        # if we already reauthorized AND we couldn't get the stream show an
        # "I give up" type of error
        if reauth:
            xbmcgui.Dialog().ok(getString(30006), getString(30007))
            return

        # if we have not reauthorized, try to authorize again
        if not authorize(onesoccer):
            xbmcgui.Dialog().ok(getString(30004), getString(30005))
            return
        return playVideo(onesoccer, data, True)

    labels = getLabels(data)
    item = xbmcgui.ListItem(labels['title'], path=url)
    item.setInfo(type="Video", infoLabels=labels)
    xbmcplugin.setResolvedUrl(addon_handle, True, item)

    return None

onesoccer = OneSoccer()

if len(sys.argv[2]) == 0:
    createMainMenu(onesoccer)
else:
    # get the dict, and then make the items not lists
    data = urlparse.parse_qs(sys.argv[2][1:])
    data = dict((name, value[0]) for name, value in data.items())
    log(data, True)
    if 'menu' in data:
        json_data = json.loads(data['menu'])
        createSubMenu(onesoccer, json_data)
    else:
        #if 'video' in data:
        playVideo(onesoccer, data)
