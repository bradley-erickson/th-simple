import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests

import components.deck_label
import components.navbar
import components.patreon
import components.podcast_card
import utils.data
import utils.date
import utils.podcasts

description = 'Discover Trainer Hill: The ultimate Pokémon '\
    'TCG analytics platform. Dive into meta analysis, deck '\
    'insights, and unique strategy tools for players.'

_prefix = 'home'
_archetype_store = f'{_prefix}-deck-store'
_meta_children = f'{_prefix}-meta-children'
_decklist_children = f'{_prefix}-decklist-children'
_podcast_children = f'{_prefix}-podcast-children'

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Trainer Hill',
    description=description
)

external_tools = {
    'City League Analysis': {'href': 'https://city.trainerhill.com/', 'icon': 'fa-city'}
}


def create_card(c):
    card = dbc.Card(dcc.Link([
        dbc.CardHeader([
            html.H2(c['title'])
        ], className=c['id']),
        dbc.CardBody([
            c['children'],
            html.Div(dbc.Spinner(id=c['computed_children']), className='text-center')
        ]),
    ], href=c['link'], id={'type': components.navbar.link_with_game, 'index': f'{c["id"]}-home'}), className='home-card h-100')
    return dbc.Col(card, md=6)


cards = [
    {'title': 'Meta Overview', 'link': '/meta', 'image': 'meta-analysis.png', 'computed_children': _meta_children, 'id': 'meta',
     'children': html.P('Unlock the secrets of the Pokémon TCG meta - Top 8 insights, matchup analysis, and more.')},
    {'title': 'Decklists Analysis', 'link': '/decklist', 'image': 'decklist-analysis.png', 'computed_children': _decklist_children, 'id': 'decklist',
     'children': html.P('Explore card breakdowns, usage trends, and matchup data for your favorite Pokémon TCG archetypes.')},
]


def create_tool(title, t, external=False):
    if external:
        availability_request = requests.get(t['href'])
        if availability_request.status_code != 200:
            return ''
    tool = dcc.Link(
        dbc.Card([
            html.H3(className=f'fas {t["icon"]}'),
            html.Div([title, html.I(className='ms-1 fas fa-arrow-up-right-from-square') if external else ''])
        ], body=True, class_name='home-card text-center'),
        href=t['href'], className='text-decoration-none', target='_blank' if external else '',
        id={'type': components.navbar.link_with_game, 'index': f'{title}-home'}
    )
    return dbc.Col(tool, sm=6, md=4)


def create_podcast_card():
    return dbc.Card([
        dbc.CardHeader(html.A('Latest Podcast Episodes', href='/tools/podcast-hub')),
        dbc.CardBody(dbc.Spinner([], id=_podcast_children))
    ])


def layout():
    main_pages = dbc.Row([
        create_card(c) for c in cards
    ], justify='around', align='stretch', class_name='g-1')
    tool_pages = {page['title']: {'href': page['path'], 'icon': page['icon']} for page in dash.page_registry.values() if page['path'].startswith('/tools/')}
    sorted_tools = sorted(tool_pages.keys())
    tools = dbc.Row([
        create_tool(k, tool_pages[k]) for k in sorted_tools if k != 'Podcast Hub'
    ] + [
        # create_tool(k, external_tools[k], external=True) for k in external_tools
    ], justify='around', class_name='gy-2 mt-1 mb-2')
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                main_pages,
                tools
            ],lg=7, xl=8),
            dbc.Col(create_podcast_card(),lg=5, xl=4)
        ], class_name='mb-1'),
        components.patreon.patreon_banner,
        dcc.Store(id=_archetype_store, data=[])
    ], id=_prefix)


@callback(
    Output(_archetype_store, 'data'),
    Input(_prefix, 'id'),
    Input(components.navbar.game_preference, 'value')
)
def update_decks(_, game):
    deck_data = utils.data.get_decks({'start_date': utils.date.weeks_ago_3(), 'game': game})
    data = {d['id']: d for d in deck_data[:6] if d['id'] != 'other'}
    return data


def create_matchup_progress_bar(matchup, decks):
    bar = dbc.Progress([
        dbc.Progress(value=matchup['wins'], color='danger', bar=True, label=f"{matchup['wins']/matchup['total']:.0%}"),
        dbc.Progress(value=matchup['ties'], color='light', bar=True),
        dbc.Progress(value=matchup['losses'], color='info', bar=True, label=f"{matchup['losses']/matchup['total']:.0%}")
    ], max=matchup['total'])
    component = html.Div([
        html.Div([
            components.deck_label.format_label(decks[matchup['deck1']], hide_text=True),
            'vs',
            components.deck_label.format_label(decks[matchup['deck2']], hide_text=True),
        ], className='d-flex justify-content-between align-items-center'),
        bar,
    ], className='mb-2')
    return component


@callback(
    Output(_meta_children, 'children'),
    Input(_archetype_store, 'data'),
    Input(components.navbar.game_preference, 'value')
)
def update_meta_children(archetypes, game):
    decks = archetypes.keys()
    matchup_data = utils.data.fetch_matchup_data({'start_date': utils.date.weeks_ago_3(), 'game': game}, decks)
    filtered_data = (d for d in matchup_data if d['deck1'] != d['deck2'])
    sorted_data = sorted(filtered_data, key=lambda d: d['total'], reverse=True)
    children = [html.H5('Common Matchups')]
    used_decks = []
    for matchup in sorted_data:
        deck_pair = matchup['deck2'] + matchup['deck1']
        if deck_pair in used_decks: continue
        children.append(create_matchup_progress_bar(matchup, archetypes))
        used_decks.append(matchup['deck1'] + matchup['deck2'])
        if len(used_decks) > 2: break
    return children


@callback(
    Output(_decklist_children, 'children'),
    Input(_archetype_store, 'data'),
)
def update_decklist_children(archetypes):
    decks = list(archetypes.keys())
    component = html.Div([
        html.Div([
            f'{i+1}.',
            html.Span(components.deck_label.format_label(archetypes[d]), className='ms-1 d-inline-block')
        ], className='text-start d-flex align-items-center mb-1') for i, d in enumerate(decks[:5])
    ])
    return component


@callback(
    Output(_podcast_children, 'children'),
    Input(_prefix, 'id'),
)
def update_decklist_children(id):
    episodes = utils.podcasts.fetch_latest_episodes()[:3]
    podcasts = [components.podcast_card.create_podcast_card(pod) for pod in episodes]
    return podcasts
