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
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    logger.info(f"Authorize url = {rv}")
    return rv


@api.route("/authorize")
def authorize(req, resp):
    """Redirect user to the Strava Authorization page"""
    api.redirect(resp, location=authorize_url())


@api.route("/athlete")
def athlete(req, resp):
    _id = req.params.get('id', None)
    logger.info(f"Athlete id is {_id}")
    dir_name = os.path.join(os.path.expanduser('~'), '.stravadata')
    f_name = os.path.join(dir_name, f"athlete_{_id}.json")
    try:
        with open(f_name, 'r') as f:
            a = json.load(f)
            rv = {'firstname': a['firstname'],
                  'lastname': a['lastname'],
                  'ftp': a.get('ftp', None),
                  'id': _id}
    except Exception as e:
        logger.warning(e)
        rv = None
    resp.media = rv


@api.route("/data")
def data(req, resp):
    id = req.params.get('id', None)
    dir_name = os.path.join(os.path.expanduser('~'), '.testdata')
    f_name = os.path.join(dir_name, f'{id}.json')
    logger.debug(f"Trying to read data from {f_name}")
    try:
        with open(f_name, 'r') as f:
            logger.debug(f'Loading json from {f_name}')
            resp.media = json.load(f)
    except Exception as e:
        logger.warning(e)
        logger.debug('Data are not redy to load')
        resp.media = []
    

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
    logger.info(f"authorization succesful {response}")
    load_athlete(response)
    load_activities(response)
    app_url = os.getenv('APP_URL', 'http://localhost:5042')
    api.redirect(resp, location=f"{app_url}/{response['athlete']['id']}")


# @api.background.task
def load_athlete(response):
    client = stravaio.StravaIO(response["access_token"])
    athlete = client.get_logged_in_athlete()
    athlete.store_locally()
    logger.debug('load athlete')


@api.background.task
def load_activities(response):
    client = stravaio.StravaIO(response["access_token"])
    def extract():
        """Fetch activities summary from Strava"""
        activities = None
        while activities is None:
            time.sleep(1)
            try:
                activities = client.get_logged_in_athlete_activities(after='20180101')
            except:
                activities = None
        logger.debug('load_activities: extract: fetching activities')
        for a in activities:
            yield a

    def get_streams(a):
        """Returns dict of activitiy and streams dataframe"""
        if (a.device_watts): # check if the activity has the power data
            logger.debug(f'load_activities: Fetching stream for {maya.parse(a.start_date).iso8601()}:, {a.name}, {a.start_latlng}, {a.trainer}, {a.type}')
            s = client.get_activity_streams(a.id, response['athlete']['id'])
            if isinstance(s, pd.DataFrame): # check whether the stream was loaded from the local copy
                logger.debug(f'load_activities     ...found locally')
                _s = s
            else: # Streams were loaded from the API, will be stored locally first
                logger.debug(f'load_activities     ...fetched remotely, storing locally')
                s.store_locally()
                _s = pd.DataFrame(s.to_dict())
            yield {maya.parse(a.start_date).iso8601(): list(_s['watts'])}

    d = []
    def load(s):
        logger.debug('load_activities: Appending date and power data to the dict')
        d.append(s)

    g = bonobo.Graph()
    g.add_chain(extract, get_streams, load)
    bonobo.run(g)

    f_name = f"{response['athlete']['id']}.json"
    with open(os.path.join(dir_testdata(), f_name), 'w') as f:
        logger.debug(f'load_activities: Save data to json {f_name}')
        json.dump(d, f)


def dir_testdata():
    home_dir = os.path.expanduser('~')
    strava_dir = os.path.join(home_dir, '.testdata')
    if not os.path.exists(strava_dir):
        os.mkdir(strava_dir)
    return strava_dir



if __name__ == "__main__":
    api.run(address="0.0.0.0")
