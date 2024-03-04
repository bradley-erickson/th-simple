import dash
from dash import html, callback, Output, Input
import dash_bootstrap_components as dbc
import datetime
import requests
import xml.etree.ElementTree as ET

from utils import cache

description = 'Stay tuned with our Pokémon TCG Podcast Hub: Latest episodes from top shows. Dive into insightful discussions for TCG enthusiasts.'

dash.register_page(
    __name__,
    path='/tools/podcast-hub',
    title='Podcast Hub',
    icon='fa-podcast',
    description=description
)

prefix = 'podcasts'
container = f'{prefix}-container'

FEEDS = {
    'Uncommon Energy': 'https://anchor.fm/s/8755b1a8/podcast/rss',
    'Lake of Rage': 'https://anchor.fm/s/520e10bc/podcast/rss',
    'Tag Team Podcast': 'https://anchor.fm/s/d9148280/podcast/rss',
    'Meta Pod': 'https://anchor.fm/s/238c39d0/podcast/rss',
    'Beach Court': 'https://audioboom.com/channels/5112218.rss',
    'Shift Gear': 'https://feeds.captivate.fm/the-shift-gear-podcast/',
    'Trashalanche': 'https://feeds.buzzsprout.com/1261064.rss',
    'Drew Too Many': 'https://anchor.fm/s/d411e804/podcast/rss',
    # 'FlowTKast': 'https://anchor.fm/s/3f94e654/podcast/rss',
    # 'Experience Share': '',
    # 'Lost Mine': '',
    'Pittsburgh Pokemon': 'https://anchor.fm/s/2a98f524/podcast/rss',
    'Dead Draw Gaming': 'https://feeds.buzzsprout.com/1187012.rss'
}

BACKUP = {
    'Trashalanche': 'https://www.trashalanche.com/',
    'Dead Draw Gaming': 'https://feeds.buzzsprout.com/1187012'
}

# cache for half an hour
@cache.cache.memoize(timeout=1800)
def download_rss_feed(url):
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error downloading RSS feed. Status Code: {response.status_code}")
        return None
    

def get_link(item):
    link = item.find('link')
    if link is not None:
        return link.text
    link = item.find('url')
    if link is not None:
        return link.text
    return None


def parse_rss_feed_for_first_item(xml_content):
    if xml_content:
        # Parse XML content
        root = ET.fromstring(xml_content)
        image = root.find(".//channel/image/url").text
        # Iterate through items and return single
        for item in root.findall(".//channel/item"):
            title = item.find("title").text
            summary = item.find("description").text
            link = get_link(item)
            published_date = convert_published_to_datetime(item.find("pubDate").text)

            return {'title': title,'summary': summary, 'link': link,
                    'published': published_date, 'image': image}


def fetch_latest_episodes():
    episodes = []
    for key in FEEDS:
        rss_feed_url = FEEDS[key]
        xml_content = download_rss_feed(rss_feed_url)
        if xml_content:
            first = parse_rss_feed_for_first_item(xml_content)
            first['podcast_title'] = key
            episodes.append(first)
    return episodes


def convert_published_to_datetime(item):
    try:
        # Try the first date format
        dt = datetime.datetime.strptime(item, '%a, %d %b %Y %H:%M:%S %Z')
    except ValueError:
        # If the first format fails, try the second date format
        dt = datetime.datetime.strptime(item, '%a, %d %b %Y %H:%M:%S %z')

    # Convert the datetime to UTC timezone
    return dt.astimezone(datetime.timezone.utc)


def create_podcast_card(pod):
    url = pod['link'] if pod['link'] is not None else BACKUP[pod['podcast_title']]
    large_card = dbc.Card(html.A([
        dbc.Row([
            dbc.Col(dbc.CardImg(
                src=pod['image'],
                class_name='img-fluid rounded-start ms-1 my-1'
            ), xs=2, md=3),
            dbc.Col(dbc.CardBody([
                html.H5(pod['title']),
                html.Div(pod['podcast_title'], className='text-muted'),
                html.Small(pod['published'].strftime('%a %b %D %Y at %H:%M %Z'), className='text-muted'),
            ], class_name='text-decoration-none'), xs=10, md=9)
        ], className='g-0 h-100 d-flex align-items-center')
    ], href=url, target='_blank', className='text-decoration-none'), class_name='h-100 d-none d-md-block')

    small_card = dbc.Card(html.A([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dbc.CardImg(
                    src=pod['image'],
                    class_name='img-fluid rounded-start'
                ), xs=2),
                dbc.Col([
                    html.Div(pod['podcast_title'], className='text-muted'),
                    html.Small(pod['published'].strftime('%a %b %D %Y at %H:%M %Z'), className='text-muted'),
                ], xs=10)
            ], className='g-2 h-100 d-flex align-items-center'),
            html.H5(pod['title'])
        ])
    ], href=url, target='_blank', className='text-decoration-none'), class_name='h-100 d-md-none')

    card = html.Div([
        large_card,
        small_card
    ], className='h-100')
    return card


def layout():
    cont = html.Div([
        html.H2('Podcast Hub'),
        dbc.Spinner(id=container),
        html.Div(html.Small([
            'If we are ',
            html.Strong('missing'),
            ' a podcast, please submit a ',
            html.A('Feedback Form', href='/feedback'),
            " with the podcast's name and we'll get it added!"
        ]))
    ])
    return cont


@callback(
    Output(container, 'children'),
    Input(container, 'className')
)
def update_podcasts(_):
    episodes = fetch_latest_episodes()
    episodes = sorted(episodes, key=lambda x: x['published'], reverse=True)
    return dbc.Row([
        dbc.Col(
            create_podcast_card(pod),
            md=6, xxl=4,
            class_name='align-self-stretch'
        ) for pod in episodes
    ], class_name='g-1')
