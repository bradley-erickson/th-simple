import dash
from dash import exceptions, clientside_callback, ClientsideFunction, html, dcc, callback, Output, Input, State, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import urllib

from components import (tour_filter, deck_label,
    card_table, matchup_table, trend_graph, download_button,
    placement as _placement, loading)
from utils import data, url, cards as _cards, cache, images

dash.register_page(
    __name__,
    path_template='/decklist/<deck>',
    title='Decklist Analysis',
    image='decklist-analysis.png',
    description='Explore Pokémon TCG Decklists: In-depth analysis of deck '\
        'archetypes, card trends, and matchup impacts for strategic '\
        'deck building.'
)

prefix = 'decklist'
store = f'{prefix}-store'
title = f'{prefix}-title'
deck_count = f'{prefix}-deck-count'
option_store = f'{prefix}-option-store'

decklist_filters = f'{prefix}-filters'
filters_collapse = f'{decklist_filters}-collapse'
card_select = f'{decklist_filters}-card-select'
exclude_select = f'{decklist_filters}-exclude-card-select'
granularity_slider = f'{decklist_filters}-granularity'
placement_select = f'{decklist_filters}-placement'

list_tooltip = f'{prefix}-table-tooltip'

skel_loading = f'{prefix}-skeleton-loading'
loading_text = f'{prefix}-loading-text'
table_view = f'{prefix}-table-view'
table_store = f'{prefix}-table-store'
table_clipboard = f'{prefix}-table-clipboard'
table_clip_btn = f'{prefix}-table-clipboard-btn'
download_image = f'{prefix}-download-image'
card_table_id = f'{prefix}-card-table'

card_matchups = f'{prefix}-card-matchups'
card_trend = f'{prefix}-card-trend'

skel_disable = f'{prefix}-skeleton-disable'
trend_disable = f'{prefix}-trend-disable'
matchup_disable = f'{prefix}-matchup-disable'

overview_header = f'{prefix}-list-overview-header'
individual_card_header = f'{prefix}-matchup-header'
headers = {
    k: {'header': k, 'collapse': f'{k}-collapse'} for k in [overview_header, individual_card_header]
}

def create_filter(include, exclude, granularity, placement):

    filter_row = dbc.Card([
        html.A(
            dbc.CardHeader([
                html.I(className='fas fa-filter me-1'),
                'Decklist Filters'
            ]),
            id=decklist_filters
        ),
        dbc.Collapse(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Includes Card'),
                        dcc.Dropdown(id={'type': card_select, 'index': 'include'}, searchable=True, value=include)
                    ], md=6, lg=4, xl=3),
                    dbc.Col([
                        dbc.Label('Excludes Card'),
                        dcc.Dropdown(id=exclude_select, searchable=True, value=exclude)
                    ], md=6, lg=4, xl=3),
                    dbc.Col([
                        dbc.Label('Granularity'),
                        dcc.Slider(
                                id=granularity_slider,
                                value=float(granularity),
                                min=0.5, max=1, step=0.1,
                                marks={
                                    0.5: '50%', 0.6: '60%', 0.7: '70%',
                                    0.8: '80%', 0.9: '90%', 1: '100%'
                                }
                            )
                    ], md=6, lg=4, xl=3),
                    dbc.Col([
                        dbc.Label('Placement'),
                        _placement.create_placement_dropdown(placement_select, placement)
                    ], md=6, lg=4, xl=3)
                ], className='mb-1')
            ]),
            id=filters_collapse
        )
    ])
    return filter_row

def layout(deck=None, players=None, start_date=None, end_date=None, platform=None, include=None, exclude=None, granularity=0.6, placement=0.5):
    include = None if include == 'None' else include
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, platform, prefix)
    filters = tour_filter.create_tour_filter(players, start_date, end_date, platform)
    filters['deck'] = deck
    filters['placement'] = placement
    filters['include'] = include
    filters['exclude'] = exclude
    filters['granularity'] = granularity

    change_deck_url = f'/decklist{tour_filter.create_param_string(filters)}'
    cont = html.Div([
        html.H2('Decklist Analysis'),
        tours,
        create_filter(include, exclude, granularity, placement),
        dcc.Store(id=store, data=filters),
        dcc.Store(id=option_store, data=[]),
        html.Div([
            html.H3([
                html.Span(deck, id=title, className='d-flex'),
                dbc.Spinner(dbc.Badge(0, id=deck_count, className='ms-1'), type='grow')
            ], className='d-flex mb-0'),
            html.Div([
                dbc.Button([
                    html.I(className='fas fa-list'),
                    html.Span('Change deck', className='ms-1 d-lg-inline-block d-none')
                ], href=change_deck_url, title='Change deck')
            ], className='d-flex')
        ], className='d-flex justify-content-between align-items-center mt-1'),
        html.Span(loading.random_message(), id=loading_text),
        html.Div([
            html.A(html.H4([
                'List Overview',
            ]), id=headers[overview_header]['header']),
            html.Div([
                download_button.DownloadImageAIO(aio_id=download_image, dom_id=headers[overview_header]['collapse'], className='me-1 d-inline-block'),
                dbc.Button(dcc.Clipboard(id=table_clipboard, content='None'), className='me-1', title='Copy Skeleton Decklist', id=table_clip_btn),
                html.Span(dbc.RadioItems(
                    id=table_view,
                    className='btn-group align-baseline',
                    inputClassName='btn-check',
                    labelClassName='btn btn-outline-primary',
                    labelCheckedClassName='active',
                    options=[
                        {'label': html.I(className='fas fa-table-cells', title='Grid view'), 'value': 'grid'},
                        {'label': html.I(className='fas fa-bars', title='List view'), 'value': 'list'},
                    ],
                    value='grid',
                ), className='radio-group'),
            ]),
            dcc.Store(id=table_store, data={'total': 0, 'cards': []}),
            html.Button(id=skel_disable, className='d-none')
        ], className='d-flex justify-content-between align-items-center'),
        dbc.Collapse([
            dbc.Alert(['Loading skeleton analysis.'], id=skel_loading, is_open=False, color='warning'),
            dbc.Spinner(id=card_table_id),
        ], id=headers[overview_header]['collapse'], is_open=True),
        html.A(html.H4('Individual Card Analysis'), id=headers[individual_card_header]['header']),
        dbc.Collapse(
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(id={'type': card_select, 'index': 'individual'}, searchable=True, value=include),
                            xs={'order': 'last', 'size': 9},
                            lg={'order': 'first', 'size': 12}
                        ),
                        dbc.Col(
                            html.Img(src=images.get_card_image(include, 'SM'), className='w-100') if include else [],
                            xs=3, lg=12
                        )
                    ]),
                ], lg=2),
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(dbc.Spinner(id=card_trend), label='Trend'),
                        dbc.Tab(dbc.Spinner(id=card_matchups), label='Matchups')
                    ], id='individual-card-tabs', active_tab='tab-0'),
                    html.Small('* Excluded cards are NOT included in this analysis.')
                ], lg=10),
                html.Button(id=trend_disable, className='d-none'),
                html.Button(id=matchup_disable, className='d-none')
            ]),
            id=headers[individual_card_header]['collapse'],
            is_open=True
        )
    ])
    return cont

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(filters_collapse, 'is_open'),
    Input(decklist_filters, 'n_clicks'),
    State(filters_collapse, 'is_open')
)

for k in headers.keys():
    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
        Output(headers[k]['collapse'], 'is_open'),
        Input(headers[k]['header'], 'n_clicks'),
        State(headers[k]['collapse'], 'is_open')
    )


@callback(
    Output(title, 'children'),
    Output(option_store, 'data'),
    Input(store, 'data'),
    State(option_store, 'data')
)
def update_title(tf, current):
    if len(current) > 0:
        raise exceptions.PreventUpdate
    deck = tf['deck']
    decks = data.get_decks(tf)
    deck = urllib.parse.unquote(deck)
    try:
        label = deck_label.format_label(next(d for d in decks if d['id'] == deck))
    except StopIteration:
        label = f'Deck {deck} not found.'
    return label, decks


@callback(
    Output({'type': card_select, 'index': ALL}, 'options'),
    Output(exclude_select, 'options'),
    Input(store, 'data')
)
@cache.cache.memoize()
def update_card_select_options(tour_filters):
    url = f'{data.api_url}/cards/{tour_filters["deck"]}'
    r = data.session.get(url, params=tour_filters)
    if r.status_code == 200:
        cards = r.json()
        formatted_cards = [{
            'value': c['card_code'],
            'label': f'{c["name"]} {c["card_code"]}',
            'search': c['name']
        } for c in cards]
        return [formatted_cards, formatted_cards], formatted_cards
    return [[], []], []


@callback(
    Output('_pages_location', 'search'),
    Input({'type': card_select, 'index': ALL}, 'value'),
    Input(exclude_select, 'value'),
    Input(granularity_slider, 'value'),
    Input(placement_select, 'value'),
    State(store, 'data')
)
def update_search(include, exclude, granularity, placement, tf):
    params = tf.copy()
    params_str = tour_filter.create_param_string(params)
    
    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('index', '') in ['include', 'individual']:
        if ctx.triggered_id['index'] == 'include':
            params_str += f'&include={include[0]}'
        else:
            params_str += f'&include={include[1]}'
    if exclude is not None:
        params_str += f'&exclude={exclude}'
    if granularity is not None:
        params_str += f'&granularity={granularity}'
    params_str += f'&placement={placement}'
    return params_str

@callback(
    Output(table_store, 'data'),
    Output(deck_count, 'children'),
    Input(store, 'data'),
    running=[
        (Output(skel_disable, 'disabled'), True, False),
    ],
    background=True
)
def update_table_store(tf):
    url = f'{data.analysis_url}/decklists/{tf["deck"]}/skeleton-counts'
    params = tf.copy()
    if 'include' in tf:
        params['include_card'] = tf['include']
    if 'exclude' in tf:
        params['exclude_card'] = tf['exclude']
    params['granularity'] = tf['granularity']
    r = data.session.post(url, params=params)
    out = {'cards': [], 'total': 0}
    if r.status_code == 200:
        resp = r.json()
        out['cards'] = resp['data']
        out['total'] = resp['total']
    return out, out['total']


@callback(
    Output(card_table_id, 'children'),
    Output(table_clipboard, 'content'),
    Input(table_view, 'value'),
    Input(table_store, 'data')
)
def update_card_table(view, data):
    skeleton = [c for c in data['cards'] if c['skeleton']]
    skeleton_list = '\n'.join((' '.join(str(c[k]) for k in ['count', 'name', 'set', 'number']) for c in skeleton))
    return card_table.container_layout[view](data['cards'], data['total']), skeleton_list


@callback(
    Output(card_matchups, 'children'),
    Input(store, 'data'),
    Input(option_store, 'data'),
    running=[
        (Output(matchup_disable, 'disabled'), True, False)
    ],
    background=True
)
@cache.cache.memoize()
def update_card_matchups(tf, options):
    if tf['include'] is None:
        return html.Div()
    
    if len(options) == 0:
        raise exceptions.PreventUpdate
    url = f'{data.analysis_url}/decklists/{tf["deck"]}/card-matchups/{tf["include"]}'
    params = tf.copy()
    params['against_archetypes'] = [o['id'] for o in options[:15]]
    if 'other' in params['against_archetypes']: params['against_archetypes'].remove('other')
    params['against_archetypes'].remove(tf['deck'])
    r = data.session.post(url, params=params)
    matchups = []
    if r.status_code == 200:
        matchups = r.json()['data']

    decks = {d['name']: d for d in options}
    return matchup_table.create_matchup_spread(matchups, decks, player='count', against='deck_other')


@callback(
    Output(card_trend, 'children'),
    Input(store, 'data'),
    running=[
        (Output(trend_disable, 'disabled'), True, False)
    ],
    background=True
)
def update_card_trends(tf):
    if tf['include'] is None:
        return html.Div()
    
    url = f'{data.analysis_url}/decklists/{tf["deck"]}/trend/{tf["include"]}'
    r = data.session.post(url, params=tf)
    trend = []
    if r.status_code == 200:
        trend = r.json()['data']

    df = pd.DataFrame.from_records(
        trend,
        columns=['date', 'card_count', 'counts', 'percent']
    )

    return trend_graph.create_trend_graph(df)


@callback(
    Output({'type': card_select, 'index': ALL}, 'disabled'),
    Output(exclude_select, 'disabled'),
    Output(granularity_slider, 'disabled'),
    Output(placement_select, 'disabled'),
    Output(loading_text, 'className'),
    Input(skel_disable, 'disabled'),
    Input(trend_disable, 'disabled'),
    Input(matchup_disable, 'disabled'),
)
def disable_inputs(s, t, m):
    disabled = s or t or m
    classname = 'd-none' if not disabled else 'fs-6'
    return [disabled, disabled], disabled, disabled, disabled, classname
