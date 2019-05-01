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
    xbmc.log('MICAH menu is {}'.format(menu), xbmc.LOGWARNING)
    for m in menu:
        xbmc.log('MICAH menu item is {}'.format(m), xbmc.LOGWARNING)
        labels = {'title': m['title'], 'mediatype': 'video'}
        item = xbmcgui.ListItem(labels['title'])
        item.setInfo('Video', labels)
        item.setProperty('IsPlayable', 'true')

        if m['live']:
            log('MICAH createSubMenu LIVE {}'.format(m['live']), True)
        else:
            log('MICAH createSubMenu NOT LIVE {}'.format(m['live']), True)

        # non-live video uses mongoId
        values = {'title': m['title'], 'video': m['id'] if m['live'] else m['mongoId'], 'live': m['live']}
        path = sys.argv[0] + "?" + urllib.urlencode(values)
        xbmcplugin.addDirectoryItem(addon_handle, path, item, False)
    xbmcplugin.endOfDirectory(addon_handle)
    return None

def playVideo(onesoccer, data, reauth=False):
    xbmc.log('MICAH video data is {}'.format(data), xbmc.LOGWARNING)
    video = data['video'][0]
    title = data['title'][0]
    live = data['live'][0]
    if live:
        log('MICAH LIVE {}'.format(live), True)
    else:
        log('MICAH NOT LIVE {}'.format(live), False)
    try:
        url = onesoccer.getManifest(video, live.lower() == 'true')
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
    xbmc.log('MICAH manifest is {}'.format(url), xbmc.LOGWARNING)

    labels = {'title': title, 'mediatype': 'video'}
    item = xbmcgui.ListItem(title, path=url)
    #item.setArt({ 'thumb': image, 'poster': image })
    item.setInfo(type="Video", infoLabels=labels)
    # helper = inputstreamhelper.Helper('hls')
    # if not xbmcaddon.Addon().getSettingBool("ffmpeg") and helper.check_inputstream():
    #     item.setProperty('inputstreamaddon','inputstream.adaptive')
    #     item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    xbmcplugin.setResolvedUrl(addon_handle, True, item)

    return None

onesoccer = OneSoccer()

if len(sys.argv[2]) == 0:
    createMainMenu(onesoccer)
else:
    data = urlparse.parse_qs(sys.argv[2][1:])
    xbmc.log('MICAH data is {}'.format(data), xbmc.LOGWARNING)
    if 'menu' in data:
        json_data = json.loads(data['menu'][0])
        createSubMenu(onesoccer, json_data)
    elif 'video' in data:
        playVideo(onesoccer, data)
