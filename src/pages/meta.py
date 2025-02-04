import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import datetime
import pandas as pd

from components import (
    tour_filter, deck_label, matchup_table, placement,
    download_button, breakdown as _breakdown, help_icon,
    feedback_link
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

_help_icon = f'{prefix}-help'
_help_children = html.Ul([
    html.Li([html.Strong('Filter:'), ' Select which types of tournaments you wish to see.']),
    html.Li([html.Strong('Breakdown:'), ' View the overall distribution of deck archetypes and analyze top performers.']),
    html.Li([html.Strong('Matchups:'), ' Explore detailed head-to-head comparisons between deck archetypes.']),
    feedback_link.list_item,
], className='mb-0')

breakdown = f'{prefix}-breakdown'
breakdown_place = f'{prefix}-breakdown-placement'
breakdown_overall = f'{prefix}-breakdown-overall'
breakdown_overall_wrap = f'{prefix}-breakdown-overall-wrap'
breakdown_specific = f'{prefix}-breakdown-specific'
breakdown_specific_wrap = f'{prefix}-breakdown-specific-wrap'
breakdown_show_more = f'{prefix}-breakdown-show-more'
_breakdown_help = f'{breakdown}-help'
_breakdown_children = [
    html.Div('Rankings based on percentage in meta.'),
    html.Div([
        'Trends are based on usage during the last third of the selected date range.',
        dbc.Progress([
            dbc.Progress(value=66, color='secondary', bar=True, label='A'),
            dbc.Progress(value=34, color='primary', bar=True, label='B')
        ], class_name='mb-1'),
        html.Div([
            _breakdown.create_deck_delta(-1),
            ' rank during ', dbc.Badge('A', color='secondary'), ' > ',
            dbc.Badge('B', color='primary')
        ], className='mb-1'),
        html.Div([
            _breakdown.create_deck_delta(1),
            ' rank during ', dbc.Badge('B', color='primary'), ' > ',
            dbc.Badge('A', color='secondary')
        ]),
    ])
]

archetype_select = f'{prefix}-archetype-select'
archetype_store = f'{prefix}-archetype-store'
download_matchups_btn = f'{prefix}-download-matchup-btn'
download_matchups = f'{prefix}-download-matchup-data'
matchup_data_store = f'{prefix}-matchup-data-store'
matchups = f'{prefix}-matchups'
placing_id = f'{prefix}-placing'
_matchups_help = f'{prefix}-matchups-help'
_matchups_children = matchup_table.example


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
        overall = r.json()['overall']
    return overall


def layout(players=None, start_date=None, end_date=None, platform=None, game=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, platform, game, prefix)
    tour_filters = tour_filter.create_tour_filter(players, start_date, end_date, platform, game)
    
    cont = html.Div([
        html.Div([
            html.H2('Meta Analysis', className='d-inline-block'),
            help_icon.create_help_icon(_help_icon, _help_children, className='align-top'),
        ]),
        dbc.Alert([
            'The Tier List Creator has moved to its own ',
            dcc.Link('Tool', href='/tools/tier-list', className='alert-link')
        ], id='tierlist-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        dbc.Alert(['Loading data from server, this may take a moment...'], id=loading, is_open=False, color='warning'),
        dcc.Store(id=tour_store, data=tour_filters),
        dcc.Store(id=archetype_store, data=[]),
        tours,
        html.Div([
            html.H3('Breakdown', id='breakdown', className='d-inline-block'),
            help_icon.create_help_icon(_breakdown_help, _breakdown_children, 'align-top')
        ]),
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(value='Overall', disabled=True, class_name='text-center'),
                    download_button.DownloadImageAIO(dom_id=breakdown_overall_wrap, button_class_name='rounded-0 rounded-end', text=False)
                ]),
                dbc.Spinner(id=breakdown_overall)
            ], id=breakdown_overall_wrap, lg=6),
            dbc.Col([
                dbc.InputGroup([
                    html.Div(placement.create_placement_dropdown(breakdown_place, 8, 'text-center'), className=' dcc-dropdown-inputgroup'),
                    download_button.DownloadImageAIO(dom_id=breakdown_specific_wrap, button_class_name='rounded-0 rounded-end', text=False)
                ]),
                dbc.Spinner(id=breakdown_specific)
            ], id=breakdown_specific_wrap, lg=6),
            dbc.Col(
                dbc.Switch(id=breakdown_show_more, label='Show more', value=False)
            )
        ]),
        html.Div([
            html.H3('Matchups', id='matchups', className='d-inline-block'),
            help_icon.create_help_icon(_matchups_help, _matchups_children, 'align-top'),
            html.Span([
                download_button.DownloadImageAIO(dom_id=matchups, className='me-1 d-inline-block', text='Download (png)'),
                dbc.Button([
                        html.I(className='fas fa-file-export'),
                        html.Span('Export data (csv)', className='d-sm-inline-block d-none ms-1')
                    ],
                    id=download_matchups_btn,
                    title='Export matchup data (csv)'),
                dcc.Download(id=download_matchups)
            ], className='float-end')
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
    Input(breakdown_show_more, 'value')
)
@cache.cache.memoize(21600)
def update_breakdown_overall(tour_filters, archetypes, show_more):
    decks = {d['value']: d['label'] for d in archetypes}

    overall = fetch_breakdown_data(tour_filters)
    breakpoint = 15 if show_more else 8
    for d in overall:
        d['label'] = decks[d['deck']]
        d['href'] = f'/decklist/{d["deck"]}{tour_filter.create_param_string(tour_filters)}'

    return _breakdown.create_ordered_list(overall[0:breakpoint])

@callback(
    Output(breakdown_specific, 'children'),
    Input(tour_store, 'data'),
    Input(archetype_select, 'options'),
    Input(breakdown_place, 'value'),
    Input(breakdown_show_more, 'value'),
    background=True,
    running=[
        (Output(breakdown_place, 'disabled'), True, False)
    ]
)
def update_breakdown(tour_filters, archetypes, place, show_more):
    decks = {d['value']: d['label'] for d in archetypes}

    top_x = fetch_breakdown_data(tour_filters, place)
    breakpoint = 15 if show_more else 8
    for d in top_x:
        d['label'] = decks[d['deck']]
        d['href'] = f'/decklist/{d["deck"]}{tour_filter.create_param_string(tour_filters)}&placement={place}'

    return _breakdown.create_ordered_list(top_x[0:breakpoint])

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
    matchup_data = data.fetch_matchup_data(tour_filters, selected)
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
