import requests, json

from .utils import log, saveAuthorization, loadAuthorization

class OneSoccerAuthError(Exception):
    def __init__(self, message):
        self.message = message
        return

class OneSoccer:

    def __init__(self):
        """
        Initialize data
        """
        self.LOGIN_URL = 'https://core.onesoccer.ca/api/v1/auth/login'
        self.LAYOUT_URL = 'https://static.onesoccer.ca/onesoccer-ott/data/layout.json'
        # first param id, second param token
        self.LIVE_STREAM_FMT = 'https://core.onesoccer.ca/api/v1/media/hls/{}/{}'
        self.STREAM_FMT = 'https://core.onesoccer.ca/api/v1/media/hls/vod/{}/{}'


    def login(self, email, password):
        """
        Login to the service
        """
        credentials = {'email':email, 'password': password}
        r = requests.post(self.LOGIN_URL, json=credentials)
        js = json.loads(r.content)

        # log an error if login fails
        if 'error' in js:
            raise OneSoccerAuthError('Unable to login: {}'.format(js['error']))
        elif not 'success' in js:
            raise('Unable to interpret login response {}'.format(js))

        saveAuthorization(js['success'])

        return True


    def getLayout(self):
        """
        Get the layout configuration
        """
        r = requests.get(self.LAYOUT_URL)
        js = json.loads(r.content)
        return js


    def getManifest(self, item_id, live):
        auth = loadAuthorization()
        if not auth:
            raise OneSoccerAuthError('ERROR: no authorization data')
        elif not 'uuid' in auth:
            raise OneSoccerAuthError('ERROR: uuid not in authorization data')
        elif not 'token' in auth:
            raise OneSoccerAuthError('ERROR: token not in authorization data')

        url = self.LIVE_STREAM_FMT if live else self.STREAM_FMT
        url = url.format(item_id, auth['uuid'])
        headers = { 'x-sessionId': auth['token'] }

        r = requests.post(url, headers=headers)
        js = json.loads(r.content)

        if 'error' in js:
            raise OneSoccerAuthError('ERROR: error returned by manifest POST "{}"'.format(js['error']))

        if not 'manifest' in js:
            raise OneSoccerAuthError('ERROR: unable to interpret manifest return')

        return js['manifest']
