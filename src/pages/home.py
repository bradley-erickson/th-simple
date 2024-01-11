import dash
from dash import html
import dash_bootstrap_components as dbc

description = 'Discover Trainer Hill: The ultimate Pokémon '\
    'TCG analytics platform. Dive into meta analysis, deck '\
    'insights, and unique strategy tools for players.'

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Trainer Hill',
    description=description
)


def create_card(c):
    card = dbc.Card([
        dbc.CardImg(src=f'/assets/{c["image"]}'),
        dbc.CardImgOverlay(html.A(dbc.CardBody([
            html.H3(c['title']),
            c['children'],
        ]), href=c['link']))
    ], color='light', className='home-card')
    return dbc.Col(card, sm=7, md=6, lg=5, xl=4, xxl=3)


cards = [
    {'title': 'Meta Overview', 'link': '/meta', 'image': 'meta-analysis.png',
     'children': html.P('Unlock the secrets of the Pokémon TCG meta - Top 8 insights, matchup analysis, and more.')},
    {'title': 'Decklists Deep Dive', 'link': '/decklist', 'image': 'decklist-analysis.png',
     'children': html.P('Explore card breakdowns, usage trends, and matchup data for your favorite Pokémon TCG archetypes.')},
    {'title': 'Tools', 'link': '/tools', 'image': 'tools.png',
     'children': html.Ul([
        html.Li(html.A('Battle Log', href='/tools/battle-log', className='text-reset')),
        html.Li(html.A('Deck Diff', href='/tools/deck-diff', className='text-reset')),
        html.Li(html.A('Tier List', href='/tools/tier-list', className='text-reset')),
    ])}
]

layout = dbc.Row([
    create_card(c) for c in cards
], class_name='gy-1')
# tool list + single card for meta and single card for decklist
