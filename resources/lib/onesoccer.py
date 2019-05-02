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


    def simplifyDatum(self, datum):
        """
        Simplify a stream description down to something more kodi friendly
        """
        values = {
            'title': datum['title'],
            'plot': datum['header'],
            'date': datum['date'],
            'id': datum['id'],
            'image': datum['images']['landscape'],
            'live': datum['live']
        }

        if 'selectedStream' in datum and datum['selectedStream'] != None:
            values['selectedStream'] = datum['selectedStream']

        if 'mongoId' in datum and datum['mongoId'] != None:
            values['mongoId'] = datum['mongoId']

        return values


    def getSelectedStreamValues(self, selected_stream):
        """
        If there is a selected stream, get it from the layout and return its
        simplified values
        """
        layout = self.getLayout()
        for group in layout:
            for data in group['data']:
                if data['id'] == selected_stream:
                    return self.simplifyDatum(data)
        return None


    def getManifest(self, values):
        auth = loadAuthorization()
        if not auth:
            raise OneSoccerAuthError('ERROR: no authorization data')
        elif not 'uuid' in auth:
            raise OneSoccerAuthError('ERROR: uuid not in authorization data')
        elif not 'token' in auth:
            raise OneSoccerAuthError('ERROR: token not in authorization data')

        if 'selectedStream' in values and values['selectedStream'] != values['id']:
            values = self.getSelectedStreamValues(values['selectedStream'])

        item_id = values['mongoId'] if 'mongoId' in values else values['id']

        # this can be boolean (selected stream) or a string (everything else)
        if values['live'] == True:
            url = self.LIVE_STREAM_FMT
        elif values['live'] == False:
            self.STREAM_FMT
        elif values['live'].lower() == 'true':
            url = self.LIVE_STREAM_FMT
        else:
            url = self.STREAM_FMT
        url = url.format(item_id, auth['uuid'])
        headers = { 'x-sessionId': auth['token'] }

        r = requests.post(url, headers=headers)
        js = json.loads(r.content)

        if 'error' in js:
            raise OneSoccerAuthError('ERROR: error returned by manifest POST "{}"'.format(js['error']))

        if not 'manifest' in js:
            raise OneSoccerAuthError('ERROR: unable to interpret manifest return')

        return js['manifest']
