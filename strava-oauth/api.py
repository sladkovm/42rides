import responder
import requests
import os
import urllib
import json
import stravaio
import time
import bonobo
import maya
import pandas as pd


api = responder.API()


def authorize_url():
    """Generate authorization uri"""
    app_url = os.getenv('APP_URL', 'http://localhost:5042')
    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "response_type": "code",
        "redirect_uri": f"{app_url}/api/authorization_successful",
        "scope": "read,profile:read_all,activity:read",
        "state": 'mystate',
        "approval_prompt": "force"
    }
    values_url = urllib.parse.urlencode(params)
    base_url = 'https://www.strava.com/oauth/authorize'
    rv = base_url + '?' + values_url
    return rv


@api.route("//")
def home(req, resp):
    resp.text = "Welcome to strava-oauth"


@api.route("/client")
def client(req, resp):
    resp.text = os.getenv('STRAVA_CLIENT_ID')


@api.route("/authorize")
def authorize(req, resp):
    """Redirect user to the Strava Authorization page"""
    api.redirect(resp, location=authorize_url())


@api.route("/authorization_successful")
async def authorization_successful(req, resp):
    """Exchange code for a user token"""
    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "client_secret": os.getenv('STRAVA_CLIENT_SECRET'),
        "code": req.params.get('code'),
        "grant_type": "authorization_code"
    }
    r = requests.post("https://www.strava.com/oauth/token", params)
    
    response = json.loads(r.text)

    @api.background.task
    def load_athlete():
        client = stravaio.StravaIO(response["access_token"])
        athlete = client.get_logged_in_athlete()
        athlete.store_locally()

        def extract():
            """Fetch activities summary from Strava"""
            activities = client.get_logged_in_athlete_activities(after='20180101')
            for a in activities:
                yield a

        def get_streams(a):
            """Returns dict of activitiy and streams dataframe"""
            if (a.device_watts): # check if the activity has the power data
        #         pprint(f'{maya.parse(a.start_date).iso8601()}:, {a.name}, {a.start_latlng}, {a.trainer}, {a.type}')
                s = client.get_activity_streams(a.id, athlete.api_response.id)
                if isinstance(s, pd.DataFrame): # check whether the stream was loaded from the local copy
                    _s = s
                else: # Streams were loaded from the API, will be stored locally first
                    s.store_locally()
                    _s = pd.DataFrame(s.to_dict())
                yield {'date': maya.parse(a.start_date).iso8601(),
                    'watts': list(_s['watts'])}


        d = []
        def load(s):
            d.append(s)

        g = bonobo.Graph()
        g.add_chain(extract, get_streams, load)
        bonobo.run(g)

        def dir_testdata():
            home_dir = os.path.expanduser('~')
            strava_dir = os.path.join(home_dir, '.testdata')
            if not os.path.exists(strava_dir):
                os.mkdir(strava_dir)
            return strava_dir
        # activities = client.get_logged_in_athlete_activities(after='20180101')
        with open(os.path.join(dir_testdata(), f'{athlete.api_response.id}.json'), 'w') as f:
            json.dump(d, f)

    load_athlete()

    app_url = os.getenv('APP_URL', 'http://localhost:5042')
    api.redirect(resp, location=f"{app_url}/{response['athlete']['id']}")


if __name__ == "__main__":
    api.run(address="0.0.0.0")
