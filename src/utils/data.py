import datetime
import os
from dotenv import load_dotenv
import requests_cache

load_dotenv()

BASE_URL = 'https://play.limitlesstcg.com/ext/dinodata'
api_url = 'https://api.trainerhill.com/api'
analysis_url = 'https://api.trainerhill.com/analysis'
api_key = {'x-api-key': os.environ['TRAINER_HILL_API_KEY']}

session = requests_cache.CachedSession(expire_after=datetime.timedelta(2), backend='filesystem', cache_name='.session-cache')
session.headers.update(api_key)

def get_decks(tour_filter):
    url = f'{api_url}/decks'
    r = session.get(url, params=tour_filter)
    if r.status_code == 200:
        return r.json()
    return []
