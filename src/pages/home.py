import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

import components.patreon
import components.deck_label
import utils.data
import utils.date

description = 'Discover Trainer Hill: The ultimate Pokémon '\
    'TCG analytics platform. Dive into meta analysis, deck '\
    'insights, and unique strategy tools for players.'

_prefix = 'home'
_archetype_store = f'{_prefix}-deck-store'
_meta_children = f'{_prefix}-meta-children'
_decklist_children = f'{_prefix}-decklist-children'

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Trainer Hill',
    description=description
)


def create_card(c):
    card = dbc.Card(dcc.Link([
        dbc.CardHeader([
            html.H2(c['title'])
        ], className=c['id']),
        dbc.CardBody([
            c['children'],
            html.Div(dbc.Spinner(id=c['computed_children']), className='text-center')
        ]),
    ], href=c['link']), className='home-card')
    return dbc.Col(card, md=6, lg=5, xl=4)


cards = [
    {'title': 'Meta Overview', 'link': '/meta', 'image': 'meta-analysis.png', 'computed_children': _meta_children, 'id': 'meta',
     'children': html.P('Unlock the secrets of the Pokémon TCG meta - Top 8 insights, matchup analysis, and more.')},
    {'title': 'Decklists Analysis', 'link': '/decklist', 'image': 'decklist-analysis.png', 'computed_children': _decklist_children, 'id': 'decklist',
     'children': html.P('Explore card breakdowns, usage trends, and matchup data for your favorite Pokémon TCG archetypes.')},
]

def create_tool(title, t):
    tool = dcc.Link(dbc.Card([
        html.H3(className=f'fas {t["icon"]}'),
        html.Div(title)
    ], body=True, class_name='home-card text-center'), href=t['href'], className='text-decoration-none')
    return dbc.Col(tool, sm=6, md=4, xl=3)

def layout():
    main_pages = dbc.Row([
        create_card(c) for c in cards
    ], justify='around', class_name='g-1')
    tool_pages = {page['title']: {'href': page['path'], 'icon': page['icon']} for page in dash.page_registry.values() if page['path'].startswith('/tools/')}
    sorted_tools = sorted(tool_pages.keys())
    tools = dbc.Row([
        create_tool(k, tool_pages[k]) for k in sorted_tools
    ], justify='around', class_name='gy-2 mt-1 mb-2')
    return dbc.Container([
        main_pages,
        tools,
        components.patreon.patreon_banner,
        dcc.Store(id=_archetype_store, data=[])
    ], id=_prefix)


@callback(
    Output(_archetype_store, 'data'),
    Input(_prefix, 'id')
)
def update_decks(_):
    deck_data = utils.data.get_decks({'start_date': utils.date.weeks_ago_3()})
    data = {d['id']: d for d in deck_data[:5]}
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
    Input(_archetype_store, 'data')
)
def update_meta_children(archetypes):
    decks = archetypes.keys()
    matchup_data = utils.data.fetch_matchup_data({'start_date': utils.date.weeks_ago_3()}, decks)
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
    Input(_archetype_store, 'data')
)
def update_decklist_children(archetypes):
    decks = list(archetypes.keys())
    component = html.Div([
        html.Div([
            f'{i+1}.',
            html.Span(components.deck_label.format_label(archetypes[d]), className='ms-1 d-inline-block')
        ], className='text-start d-flex align-items-center mb-1') for i, d in enumerate(decks[:4])
    ])
    return component
