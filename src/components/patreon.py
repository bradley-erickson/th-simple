from dash import html, Output, Input, clientside_callback
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
# from dotenv import load_dotenv
# import os
# import requests


patreon_link = 'https://www.patreon.com/trainerhill'
banner_id = 'patreon-banner-id'

# TODO uncomment this when we have more patreon subscribers!
# load_dotenv(override=True)
# ACCESS_TOKEN = os.environ['PATREON_ACCESS_TOKEN']
# CAMPAIGN_ID = os.environ['PATREON_CAMPAIGN_ID']
# BASE_URL = 'https://www.patreon.com/api/oauth2/v2/'

# headers = {
#     'Authorization': f'Bearer {ACCESS_TOKEN}'
# }
# patrons_url = f'https://www.patreon.com/api/oauth2/v2/campaigns/{CAMPAIGN_ID}/members?include=currently_entitled_tiers,user&fields[member]=full_name,patron_status'


# def fetch_patreons():
#     patrons_response = requests.get(patrons_url, headers=headers)
#     patrons = patrons_response.json()['data']
#     patron_names = [
#         patron['attributes']['full_name'] for patron in patrons
#         if patron['attributes']['patron_status'] == 'active_patron'
#     ]
#     return patron_names


# def create_patreon_card():
#     card = dbc.Card([
#         html.A(
#             html.Img(src='/assets/patreon.png'),
#             className='float-start me-1', href=patreon_link, target='_blank'
#         ),
#         html.Span([
#             html.Strong('Huge thank you to our Patreon members!'),
#             html.Br(),
#             ', '.join(fetch_patreons())
#         ])
#     ], body=True)
#     return card


patreon_banner = dbc.Alert([
    html.I(className='fab fa-patreon me-1'),
    'Help support the site on ',
    html.A('Patreon', href=patreon_link, target='_blank', className='alert-link'),
    '!'
], id=banner_id)


clientside_callback(
    '''function(theme) {
    if (theme) { return 'dark' };
    return 'light';
    }
    ''',
    Output(banner_id, 'color'),
    Input(dbt.ThemeSwitchAIO.ids.switch('navbar-theme'), 'value')
)
