import os, pickle

def getAuthorizationFile():
    """
    Get the authorization file
    """
    try:
        import xbmc, xbmcaddon
        base = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
    except:
        base = os.getcwd()

    return os.path.join(base, 'authorization')


def saveAuthorization(authorization):
    log('saving authorisation')
    with open(getAuthorizationFile(), 'wb') as f:
        pickle.dump(authorization, f)


def loadAuthorization():
    """
    Load authorization from the authorization file into an object
    @return an object
    """
    try:
        with open(getAuthorizationFile(), 'rb') as f:
            authorization = pickle.load(f)
            return authorization
    except IOError as err:
        log('Unable to load authorization: {}'.format(err), True)
        return None

    return None


def log(msg, error = False):
    """
    Log an error
    @param msg The error to log
    @param error error severity indicator
    """
    try:
        import xbmc
        full_msg = "plugin.video.onesoccer: {}".format(msg)
        xbmc.log(full_msg, level=xbmc.LOGERROR if error else xbmc.LOGINFO)
    except:
        print(msg)
