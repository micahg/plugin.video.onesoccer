import xbmc, xbmcplugin, xbmcgui, xbmcaddon, urllib, urlparse, json
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
        labels = {'title': l['title']['en'], 'mediatype': 'video'}
        item = xbmcgui.ListItem(labels['title'])
        item.setInfo('Video', labels)
        encoded_data = urllib.urlencode({'menu': json.dumps(l['data'])})
        path = sys.argv[0] + "?" + encoded_data
        xbmcplugin.addDirectoryItem(addon_handle, path, item, True)
    xbmcplugin.endOfDirectory(addon_handle)
    return None


def createSubMenu(onesoccer, menu):
    for m in menu:
        values = onesoccer.simplifyDatum(m)
        labels = {'title': values['title'], 'mediatype': 'video'}
        if 'plot' in values:
            labels['plot'] = values['plot']
            labels['plotoutline'] = values['plot']

        item = xbmcgui.ListItem(labels['title'])
        item.setInfo('Video', labels)
        item.setProperty('IsPlayable', 'true')
        if 'image' in values:
            item.setArt({ 'thumb': values['image'], 'poster': values['image'] })

        path = sys.argv[0] + "?" + urllib.urlencode(values)
        xbmcplugin.addDirectoryItem(addon_handle, path, item, False)
    xbmcplugin.endOfDirectory(addon_handle)
    return None

def playVideo(onesoccer, data, reauth=False):

    try:
        url = onesoccer.getManifest(data)
    except OneSoccerAuthError as e:
        xbmc.log(e.message, xbmc.LOGWARNING)

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

    labels = {'title': data['title'], 'mediatype': 'video'}
    item = xbmcgui.ListItem(data['title'], path=url)
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
    if 'menu' in data:
        json_data = json.loads(data['menu'])
        createSubMenu(onesoccer, json_data)
    else:
        #if 'video' in data:
        playVideo(onesoccer, data)
