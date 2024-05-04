import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import datetime
import pandas as pd

from components import (
    tour_filter, deck_label, matchup_table, placement,
    download_button, breakdown as _breakdown
)
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
loading = f'{prefix}-loading'
tour_store = f'{prefix}-tour-store'
breakdown = f'{prefix}-breakdown'
breakdown_place = f'{prefix}-breakdown-placement'
breakdown_overall = f'{prefix}-breakdown-overall'
breakdown_specific = f'{prefix}-breakdown-specific'
archetype_select = f'{prefix}-archetype-select'
archetype_store = f'{prefix}-archetype-store'
download_matchups_btn = f'{prefix}-download-matchup-btn'
download_matchups = f'{prefix}-download-matchup-data'
matchup_data_store = f'{prefix}-matchup-data-store'
matchups = f'{prefix}-matchups'
placing_id = f'{prefix}-placing'

def fetch_breakdown_data(tour_data, placing=None):
    params = tour_data.copy()
    overall = []
    if placing is not None:
        params['placement'] = placing
    else:
        params['placement'] = 10_000

    url = f'{data.analysis_url}/meta/breakdown'
    r = data.session.post(url, params=params)
    if r.status_code == 200:
        overall = r.json()['overall'][0:15]
    return overall


def fetch_matchup_data(tour_data, decks):
    params = tour_data.copy()
    params['games_played'] = 5
    params['archetypes'] = decks
    params['ids_only'] = True
    url = f'{data.analysis_url}/meta/matchups'
    r = data.session.post(url, params=params)
    if r.status_code == 200:
        return r.json()['data']
    return []


def layout(players=None, start_date=None, end_date=None, platform=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, platform, prefix)
    tour_filters = tour_filter.create_tour_filter(players, start_date, end_date, platform)
    
    cont = html.Div([
        html.H2('Meta Analysis'),
        dbc.Alert([
            'The Tier List Creator has moved to its own ',
            dcc.Link('Tool', href='/tools/tier-list', className='alert-link')
        ], id='tierlist-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        dbc.Alert(['Loading data from server, this may take a moment...'], id=loading, is_open=False, color='warning'),
        dcc.Store(id=tour_store, data=tour_filters),
        dcc.Store(id=archetype_store, data=[]),
        tours,
        html.Div([
            html.H3('Breakdown', id='breakdown', className='d-inline-block mb-0'),
            html.I(className='ms-1 fas fa-circle-info', id='breakdown-info')
        ], className='d-flex align-items-center'),
        dbc.Tooltip('The trends are based on usage during the last third of the selected time period.', target='breakdown-info'),
        dbc.Row([
            dbc.Col([
                html.H4('Overall', className='text-center'),
                dbc.Spinner(id=breakdown_overall)
            ], lg=6),
            dbc.Col([
                placement.create_placement_dropdown(breakdown_place, 8, 'text-center'),
                dbc.Spinner(id=breakdown_specific)
            ], lg=6)
        ]),
        html.Div([
            html.H3('Matchups', id='matchups', className='d-inline-block'),
            dbc.Button(
                html.I(className='fas fa-file-export'),
                id=download_matchups_btn,
                className='float-end ms-1',
                title='Export matchup data (csv)'),
            download_button.DownloadImageAIO(dom_id=matchups, className='float-end'),
            dcc.Download(id=download_matchups)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label('Placement'),
                placement.create_placement_dropdown(placing_id, 10_000)
            ], md=4, lg=3, xl=2),
            dbc.Col([
                dbc.Label('Archetype Selection'),
                dcc.Dropdown(id=archetype_select, multi=True, maxHeight=400)
            ], md=8, lg=9, xl=10)
        ], className='mb-1'),
        dbc.Spinner([
            html.Div(id=matchups),
            dcc.Store(id=matchup_data_store, data=[])
        ])
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
        'value': deck['id'],
        'search': deck['name']
    } for deck in decks_raw]
    return decks, decks_raw

@callback(
    Output(breakdown_overall, 'children'),
    Input(tour_store, 'data'),
    Input(archetype_select, 'options'),
)
@cache.cache.memoize(21600)
def update_breakdown_overall(tour_filters, archetypes):
    decks = {d['value']: d['label'] for d in archetypes}

    overall = fetch_breakdown_data(tour_filters)
    for d in overall:
        d['label'] = decks[d['deck']]
        d['href'] = f'/decklist/{d["deck"]}{tour_filter.create_param_string(tour_filters)}'

    return _breakdown.create_ordered_list(overall)

@callback(
    Output(breakdown_specific, 'children'),
    Input(tour_store, 'data'),
    Input(archetype_select, 'options'),
    Input(breakdown_place, 'value'),
    background=True,
    running=[
        (Output(breakdown_place, 'disabled'), True, False)
    ]
)
def update_breakdown(tour_filters, archetypes, place):
    decks = {d['value']: d['label'] for d in archetypes}

    top_x = fetch_breakdown_data(tour_filters, place)
    for d in top_x:
        d['label'] = decks[d['deck']]
        d['href'] = f'/decklist/{d["deck"]}{tour_filter.create_param_string(tour_filters)}&placement={place}'

    return _breakdown.create_ordered_list(top_x)

@callback(
    Output(matchup_data_store, 'data'),
    Input(tour_store, 'data'),
    Input(archetype_select, 'value'),
    Input(placing_id, 'value'),
    background=True,
    running=[
        (Output(placing_id, 'disabled'), True, False),
        (Output(archetype_select, 'disabled'), True, False)
    ]
)
def update_matchups(tour_filters, selected, place):
    tour_filters['placement'] = place
    matchup_data = fetch_matchup_data(tour_filters, selected)
    return matchup_data

@callback(
    Output(matchups, 'children'),
    Input(matchup_data_store, 'data'),
    State(archetype_store, 'data'),
)
def update_matchup_children(data, archetypes):
    decks = {d['id']: d for d in archetypes}
    return matchup_table.create_matchup_spread(data, decks)

@callback(
    Output(download_matchups, 'data'),
    Input(download_matchups_btn, 'n_clicks'),
    State(matchup_data_store, 'data')
)
def download_matchup_as_csv(n_clicks, data):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    df = pd.DataFrame.from_records(
        data,
        columns=['deck1', 'deck2', 'wins', 'losses', 'ties', 'total', 'win_rate']
    )
    return dcc.send_data_frame(df.to_csv, filename=f'trainerhill-meta-matchups-{str(datetime.date.today())}.csv', index=False)


@callback(
    Output(archetype_select, 'value'),
    Input('_pages_location', 'hash'),
    Input(archetype_select, 'options')
)
def update_archetypes_selected(hash, options):
    return [opt['value'] for opt in options[0:15] if opt['value'] != 'other']
