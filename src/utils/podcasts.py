import datetime
import requests
import xml.etree.ElementTree as ET

from utils import cache

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
    'Dead Draw Gaming': 'https://feeds.buzzsprout.com/1187012.rss',
    'PCS Pokemon': 'https://anchor.fm/s/beaa6040/podcast/rss',
    'PokeBeach': 'https://feeds.buzzsprout.com/2248143.rss',
    'SpilltheTeaCG': 'https://anchor.fm/s/f5124288/podcast/rss',
    'Memory Capsule': 'https://anchor.fm/s/d94e8ac0/podcast/rss',
    'Unfazed Facts': 'https://anchor.fm/s/f47193c4/podcast/rss',
    'TCG Royals': 'https://media.rss.com/tcg-royals-podcast/feed.xml',
    'Battle Frontier': 'https://anchor.fm/s/fbc18490/podcast/rss',
    'Gust of Wind': 'https://anchor.fm/s/8df66c8c/podcast/rss',
}

BACKUP = {
    'Trashalanche': 'https://www.trashalanche.com/',
    'Dead Draw Gaming': 'https://feeds.buzzsprout.com/1187012',
    'PokeBeach': 'https://feeds.buzzsprout.com/2248143'
}

browserlike_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'application/rss+xml, application/rdf+xml, application/atom+xml, application/xml, text/xml',
    'Accept-Language': 'en-US,en;q=0.9'
}


# cache for half an hour
@cache.cache.memoize(timeout=1800)
def download_rss_feed(url):
    response = requests.get(url, headers=browserlike_headers)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error downloading RSS feed. Status Code: {response.status_code} {url}")
        return None


def get_link(item):
    link = item.find('link')
    if link is not None:
        return link.text
    link = item.find('url')
    if link is not None:
        return link.text
    return None


def convert_published_to_datetime(item):
    try:
        # Try the first date format
        dt = datetime.datetime.strptime(item, '%a, %d %b %Y %H:%M:%S %Z')
    except ValueError:
        # If the first format fails, try the second date format
        dt = datetime.datetime.strptime(item, '%a, %d %b %Y %H:%M:%S %z')

    # Convert the datetime to UTC timezone
    return dt.astimezone(datetime.timezone.utc)


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
            first['link'] = first['link'] if first['link'] is not None else BACKUP[first['podcast_title']]
            episodes.append(first)
    episodes = sorted(episodes, key=lambda x: x['published'], reverse=True)
    return episodes
