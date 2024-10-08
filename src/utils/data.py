import datetime
import os
from dotenv import load_dotenv
import requests_cache

load_dotenv()

BASE_URL = 'https://api.trainerhill.com'
# BASE_URL = 'http://localhost:5000'
api_url = f'{BASE_URL}/api'
analysis_url = f'{BASE_URL}/analysis'
api_key = {'x-api-key': os.environ['TRAINER_HILL_API_KEY']}

session = requests_cache.CachedSession(expire_after=datetime.timedelta(1), backend='filesystem', cache_name='.session-cache')
session.headers.update(api_key)

def get_decks(tour_filter):
    url = f'{api_url}/decks'
    r = session.get(url, params=tour_filter)
    content = []
    if r.status_code == 200:
        content = r.json()
    decks = []
    ids = set()
    for c in content:
        id = c['id']
        if id in ids:
            continue
        decks.append(c)
        ids.add(id)
    return decks


def fetch_matchup_data(tour_data, decks):
    params = tour_data.copy()
    params['games_played'] = 5
    params['archetypes'] = decks
    params['ids_only'] = True
    url = f'{analysis_url}/meta/matchups'
    r = session.post(url, params=params)
    if r.status_code == 200:
        return r.json()['data']
    return []
