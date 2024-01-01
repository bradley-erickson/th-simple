import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

from components import tour_filter, deck_label, matchup_table
from utils import data, cache

dash.register_page(
    __name__,
    path='/meta',
    redirect_from=['/analysis/meta'],
    title='Meta Analysis',
    image='meta-analysis.png',
    description='Delve into Pokémon TCG Meta Overview: Get top 8 '\
        'insights, current meta breakdowns, and deck matchup data '\
        'for strategic mastery.'
)

prefix = 'meta'
tour_store = f'{prefix}-tour-store'
breakdown = f'{prefix}-breakdown'
archetype_select = f'{prefix}-archetype-select'
archetype_store = f'{prefix}-archetype-store'
matchups = f'{prefix}-matchups'

def fetch_breakdown_data(tour_data):
    overall = []
    top_8 = []
    params = tour_data.copy()
    params['placement'] = 10_000
    url = f'{data.analysis_url}/meta/breakdown'
    r = data.session.post(url, params=params)
    if r.status_code == 200:
        overall = r.json()['overall'][0:15]
    params['placement'] = 8
    r = data.session.post(url, params=params)
    if r.status_code == 200:
        top_8 = r.json()['overall'][0:15]
    return overall, top_8

def create_list_label(d, max_num, i, title):
    href = d['href']
    if title == 'Top 8':
        href += '&placement=8'
    return html.Tr([
            html.Td(f'{i+1}.'),
            html.Td(html.A(d['label'], href=href), className='text-nowrap'),
            html.Td(f'{d["percent"]:.1%}', className='text-end'),
            html.Td(dbc.Progress(value=d['percent'], max=max_num, class_name='bg-transparent'), className='w-100 d-none d-lg-table-cell')
        ], className=f'deck-row {"" if i < 8 else "d-none d-md-table-row"}')

def create_ordered_list(l, title):
    max_num = max((d['percent'] for d in l), default=0)
    return dbc.Col([
        html.H4(title, className='text-center'),
        dbc.Table(html.Tbody([
            create_list_label(d, max_num, i, title) for i, d in enumerate(l)
        ]))
    ], lg=6)

def create_overview(overall, top_8):
    return dbc.Row([
        create_ordered_list(overall, 'Overall'),
        create_ordered_list(top_8, 'Top 8')
    ])

def fetch_matchup_data(tour_data, decks):
    params = tour_data.copy()
    params['games_played'] = 10
    params['archetypes'] = decks
    params['ids_only'] = True
    url = f'{data.analysis_url}/meta/matchups'
    r = data.session.post(url, params=params)
    if r.status_code == 200:
        return r.json()['data']
    return []

def layout(players=None, start_date=None, end_date=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, prefix)
    tour_filters = tour_filter.create_tour_filter(players, start_date, end_date)
    
    cont = html.Div([
        html.H2('Meta Analysis'),
        dbc.Alert([
            'The Tier List Creator has moved to its own ',
            html.A('Tool', href='/tools/tier-list', className='alert-link')
        ], id='tierlist-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        dcc.Store(id=tour_store, data=tour_filters),
        dcc.Store(id=archetype_store, data=[]),
        tours,
        html.H3('Breakdown', id='breakdown'),
        dbc.Spinner(id=breakdown),
        html.H3('Matchups', id='matchups'),
        html.Div([
            dbc.Label('Archetype select'),
            dcc.Dropdown(id=archetype_select, multi=True),
        ], className='mb-1'),
        dbc.Spinner(id=matchups)
    ])
    return cont


@callback(
    Output(archetype_select, 'options'),
    Output(archetype_store, 'data'),
    Input(tour_store, 'data')
)
def update_options(tour_filters):
    decks_raw = data.get_decks(tour_filters)
    decks = [{
        'label': deck_label.format_label(deck),
        'value': deck['id']
    } for deck in decks_raw]
    return decks, decks_raw

@callback(
    Output(breakdown, 'children'),
    Input(tour_store, 'data'),
    Input(archetype_select, 'options')
)
@cache.cache.memoize()
def update_breakdown(tour_filters, archetypes):
    decks = {d['value']: d['label'] for d in archetypes}

    overall, top_8 = fetch_breakdown_data(tour_filters)
    for d in overall:
        d['label'] = decks[d['deck']]
        d['href'] = f'/decklist/{d["deck"]}{tour_filter.create_param_string(tour_filters)}'
    for d in top_8:
        d['label'] = decks[d['deck']]
        d['href'] = f'/decklist/{d["deck"]}{tour_filter.create_param_string(tour_filters)}'

    return create_overview(overall, top_8)

@callback(
    Output(matchups, 'children'),
    Input(tour_store, 'data'),
    Input(archetype_select, 'value'),
    State(archetype_store, 'data')
)
@cache.cache.memoize()
def update_matchups(tour_filters, selected, archetypes):
    decks = {d['id']: d for d in archetypes}
    matchup_data = fetch_matchup_data(tour_filters, selected)
    return matchup_table.create_matchup_spread(matchup_data, decks)

@callback(
    Output(archetype_select, 'value'),
    Input('_pages_location', 'hash'),
    Input(archetype_select, 'options')
)
def update_archetypes_selected(hash, options):
    return [opt['value'] for opt in options[0:12]]
