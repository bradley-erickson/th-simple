import dash
from dash import exceptions, clientside_callback, ClientsideFunction, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import urllib

import components.card_table
import components.deck_label
import components.download_button
import components.feedback_link
import components.help_icon
import components.matchup_table
import components.placement
import components.tour_filter
import components.trend_graph
import utils.cache
import utils.colors
import utils.data
import utils.images

dash.register_page(
    __name__,
    path_template='/decklist/<deck>',
    title='Decklist Analysis',
    image='decklist-analysis.png',
    description='Explore Pokémon TCG Decklists: In-depth analysis of deck '\
        'archetypes, card trends, and matchup impacts for strategic '\
        'deck building.'
)

_prefix = 'decklist-analysis'

#
_breadcrumbs = f'{_prefix}-breadcrumbs'
_filter_store = f'{_prefix}-filter-store'
_deck_options_store = f'{_prefix}-deck-options-store'
_help_icon = f'{_prefix}-help'
_help_children = html.Ul([
    html.Li([html.Strong('Filter:'), ' Select which types of tournaments and decklists you wish to see.']),
    html.Li([html.Strong('Matchups:'), ' See how the deck fairs against others.']),
    html.Li([html.Strong('Decklist:'), ' Analyze the most common card inclusions.']),
    html.Li([html.Strong('Card Analysis:'), ' Get in-dept analysis regarding specific cards.']),
    components.feedback_link.list_item('decklist'),
], className='mb-0')

# Decklist filter DOM ids
_decklist_filter = f'{_prefix}-decklist-filter'
_decklist_filter_text = f'{_decklist_filter}-text'
_decklist_filter_toggle = f'{_decklist_filter}-toggle'
_decklist_filter_collapse = f'{_decklist_filter}-collapse'
_decklist_filter_include = f'{_decklist_filter}-include-select'
_decklist_filter_exclude = f'{_decklist_filter}-exclude-select'
_decklist_filter_granularity = f'{_decklist_filter}-granularity-slider'
_decklist_filter_granularity_help = f'{_decklist_filter_granularity}-help'
_decklist_filter_placement = f'{_decklist_filter}-placement'
_decklist_filter_against_archetypes = f'{_decklist_filter}-against-archetypes'

_decklist_filter_granularity_help_children = 'Percentage cutoff for how often a card needs to be included in an archetype to appear in the skeleton list.'

# Deck analysis DOM ids
_deck = f'{_prefix}-deck'
_deck_title = f'{_deck}-title'
_deck_count = f'{_deck}-count'
_deck_matchups = f'{_deck}-matchups'
_deck_matchups_help = f'{_deck_matchups}-help'
_deck_matchups_help_childen = components.matchup_table.example

# Deck analysis decklist DOM ids
_decklist = f'{_deck}-decklist'
_decklist_skeleton_view_toggle = f'{_decklist}-skeleton-view-toggle'
_decklist_skeleton_clipboard = f'{_decklist}-skeleton-clipboard'
_decklist_skeleton_clipboard_btn = f'{_decklist}-skeleton-clipboard-btn'
_decklist_skeleton = f'{_decklist}-skeleton'

# Deck analysis card DOM ids
_card = f'{_deck}-card'
_card_none_selected = f'{_card}-none-selected'
_card_selection = f'{_card}-selection'
_card_inclusion = f'{_card}-inclusion'
_card_count_inclusion = f'{_card}-count-inclusion'
_card_trend = f'{_card}-trend'
_card_matchups = f'{_card}-matchups'
_card_matchups_help = f'{_card_matchups}-help'
_card_matchups_stats_help = f'{_card_matchups}-statistical-help'
_card_matchups_stats_help_children = [
    html.P('We use statistical tests to see if the win-rate changes significantly based on how many copies of a card are included in a deck.'),
    html.Ul([
        html.Li('Each win-rate is compared with every other win-rate using a two-proportion Z-test.'),
        html.Li('We adjust for doing many comparisons using the Bonferroni correction.')
    ]),
    html.P('Learn More:'),
    html.Ul([
        html.Li(html.A('Two-Proportion Z-Test', href='https://en.wikipedia.org/wiki/Two-proportion_Z-test', target='_blank')),
        html.Li(html.A('Bonferroni Correction', href='https://en.wikipedia.org/wiki/Bonferroni_correction', target='_blank'))
    ]),
    html.P('Note: Other factors may also contribute to win-rate differences that are not accounted for here.')
]


def create_breadcrumb_items(deck, filters):
    change_deck_url = f'/decklist{components.tour_filter.create_param_string(filters)}'
    return [
        {'label': 'Home', 'href': '/'},
        {'label': 'Decks', 'href': change_deck_url},
        {'label': deck, 'active': True}
    ]


def create_decklist_filter_text(include, exclude, granularity, placement, decks=[]):
    include_text = f' includes {include},' if include else ''
    exclude_text = f' excludes {exclude},' if exclude else ''
    placement_text = next(p['label'] for p in components.placement.OPTIONS if str(p['value']) == str(placement))
    decks_text = f' against {len(decks)} decks' if len(decks) > 0 else ''
    header_text = f' -{include_text}{exclude_text} {float(granularity):.0%} granularity, placed in {placement_text}{decks_text}'
    return header_text


def create_filter(include, exclude, granularity, placement):
    filter_row = dbc.Card([
        html.A(
            dbc.CardHeader([
                html.I(className='fas fa-filter me-1'),
                html.Strong('Decklist Filters'),
                html.Span(create_decklist_filter_text(include, exclude, granularity, placement), id=_decklist_filter_text)
            ]),
            id=_decklist_filter_toggle
        ),
        dbc.Collapse(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Includes Card'),
                        dcc.Dropdown(id=_decklist_filter_include, searchable=True, value=include)
                    ], md=6, lg=4, xl=3),
                    dbc.Col([
                        dbc.Label('Excludes Card'),
                        dcc.Dropdown(id=_decklist_filter_exclude, searchable=True, value=exclude)
                    ], md=6, lg=4, xl=3),
                    dbc.Col([
                        dbc.Label('Granularity'),
                        components.help_icon.create_help_icon(_decklist_filter_granularity_help, _decklist_filter_granularity_help_children),
                        dcc.Slider(
                                id=_decklist_filter_granularity,
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
                        components.placement.create_placement_dropdown(_decklist_filter_placement, placement)
                    ], md=6, lg=4, xl=3),
                    dbc.Col([
                        dbc.Label('Against archetypes'),
                        dcc.Dropdown(id=_decklist_filter_against_archetypes, multi=True, maxHeight=400)
                    ])
                ], className='mb-1')
            ]),
            id=_decklist_filter_collapse
        )
    ])
    return filter_row


def create_deck_analysis_layout(deck, selected_card, game):
    decklist_col = dbc.Col([
        html.Div([
            html.H4('Decklist', className='d-flex mb-0'),
            components.download_button.DownloadImageAIO(dom_id=f'{_decklist_skeleton}-image', className='ms-1', text=None),
            dbc.Button(
                dcc.Clipboard(id=_decklist_skeleton_clipboard, content='None'),
                title='Copy Skeleton Decklist',
                id=_decklist_skeleton_clipboard_btn,
                class_name='mx-1'
            ),
            html.Span(dbc.RadioItems(
                id=_decklist_skeleton_view_toggle,
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
        ], className='d-flex align-items-center'),
        html.Div(dbc.Spinner(id=_decklist_skeleton), id=f'{_decklist_skeleton}-image'),
    ], lg=7)
    card_col = dbc.Col([
        html.Div([
            html.H4('Card Analysis', className='d-flex mb-0'),
            components.download_button.DownloadImageAIO(dom_id=_card, className='ms-1', text=None),
        ], className='d-flex align-items-center'),
        dcc.Dropdown(id=_card_selection, searchable=True, value=selected_card, placeholder='Choose a Card'),
        html.Div([
            dbc.Row([
                dbc.Col(
                    html.Img(src=utils.images.get_card_image(selected_card, 'SM', game), className='w-100'),
                    sm=6, md=4
                ),
                dbc.Col([
                    html.Div([
                        'Included in ',
                        html.Strong(dbc.Spinner(id=_card_inclusion, size='sm'), className='spinner-in-strong'),
                        ' of decklists!']),
                    html.Br(),
                    dbc.Spinner(id=_card_count_inclusion),
                ], sm=6, md=8),
            ]),
            html.Div([
                html.H5('Trend'),
                dbc.Spinner(id=_card_trend)
            ]),
            html.Div([
                html.H5('Card Matchups', className='d-inline-block'),
                components.help_icon.create_help_icon(_card_matchups_help, _deck_matchups_help_childen, 'align-top'),
                html.Div(dbc.Spinner(id=_card_matchups)),
                html.H6('Statistical Tests', className='d-inline-block'),
                components.help_icon.create_help_icon(_card_matchups_stats_help, _card_matchups_stats_help_children, 'align-top'),
                html.Div([
                    '* - This count is significantly different than ',
                    html.Strong('at least one'), ' other count']),
                html.Div([
                    '** - This count is significantly different than ',
                    html.Strong('all'), ' other counts']),
            ])
        ], id=_card, className='' if selected_card else 'd-none'),
        html.Div('Select a card, to run analysis', id=_card_none_selected, className='d-none' if selected_card else '')
    ], lg=5)
    return html.Div([
        html.H3([
            html.Span(deck, id=_deck_title, className='d-flex'),
            dbc.Spinner(dbc.Badge(0, id=_deck_count, className='ms-1'), type='grow')
        ], className='d-flex'),
        # Overall matchups
        html.Div([
            html.H4('Matchups', className='d-inline-block'),
            components.help_icon.create_help_icon(_deck_matchups_help, _deck_matchups_help_childen, 'align-top'),
            html.Div(dbc.Spinner(id=_deck_matchups))
        ]),
        dbc.Row([
            decklist_col,
            card_col
        ])
    ], id=_deck)


def layout(**kwargs):
    tours = components.tour_filter.TourFiltersAIO(
        kwargs.get('players'),
        kwargs.get('start_date'),
        kwargs.get('end_date'),
        kwargs.get('platform'),
        kwargs.get('game'),
        kwargs.get('division'),
        _prefix)
    filters = components.tour_filter.create_tour_filter(**kwargs)
    game = kwargs.get('game')
    deck = kwargs.get('deck')
    placement = kwargs.get('placement', 0.5)
    include = kwargs.get('include')
    exclude = kwargs.get('exclude')
    granularity = kwargs.get('granularity', 0.6)
    selected_card = kwargs.get('selected_card')
    include = None if include == 'None' else include
    filters['deck'] = deck
    filters['placement'] = placement
    filters['include'] = include
    filters['exclude'] = exclude
    filters['granularity'] = granularity
    filters['selected_card'] = selected_card

    
    cont = html.Div([
        html.Div([
            html.H2('Decklist Analysis', className='d-inline-block'),
            components.help_icon.create_help_icon(_help_icon, _help_children, 'align-top'),
        ]),
        dbc.Breadcrumb(
            items=create_breadcrumb_items(deck, filters), id=_breadcrumbs
        ),
        tours,
        create_filter(include, exclude, granularity, placement),
        dcc.Store(id=_filter_store, data=filters),
        dcc.Store(id=_deck_options_store, data=[]),
        create_deck_analysis_layout(deck, selected_card, game)
    ])
    return cont

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(_decklist_filter_collapse, 'is_open'),
    Input(_decklist_filter_toggle, 'n_clicks'),
    State(_decklist_filter_collapse, 'is_open')
)

# Decklist filter callbacks
@callback(
    Output(_decklist_filter_text, 'children'),
    Input(_decklist_filter_include, 'value'),
    Input(_decklist_filter_exclude, 'value'),
    Input(_decklist_filter_granularity, 'value'),
    Input(_decklist_filter_placement, 'value'),
    Input(_decklist_filter_against_archetypes, 'value')
)
def update_decklist_filter_text(include, exclude, granularity, placement, decks):
    return create_decklist_filter_text(include, exclude, granularity, placement, decks)


@callback(
    Output(_decklist_filter_include, 'options'),
    Output(_decklist_filter_exclude, 'options'),
    Output(_card_selection, 'options'),
    Input(_filter_store, 'data')
)
@utils.cache.cache.memoize()
def update_card_dropdown_options(tour_filters):
    url = f'{utils.data.api_url}/cards/{tour_filters["deck"]}'
    r = utils.data.session.get(url, params=tour_filters)
    if r.status_code == 200:
        cards = r.json()
        formatted_cards = [{
            'value': c['card_code'],
            'label': f'{c["name"]} {c["card_code"]}',
            'search': c['name']
        } for c in cards]
        return formatted_cards, formatted_cards, formatted_cards
    return [], [], []

@callback(
    Output(_decklist_filter_against_archetypes, 'options'),
    Output(_decklist_filter_against_archetypes, 'value'),
    Input(_deck_options_store, 'data'),
    Input(_filter_store, 'data')
)
def update_against_archetype_options(data, tf):
    filtered_data = [d for d in data if d['id'] not in ['other', tf['deck']]]
    against_ids = [o['id'] for o in filtered_data[:15]]
    decks = [{
        'label': components.deck_label.format_label(deck),
        'value': deck['id'],
        'search': deck['name']
    } for deck in filtered_data]
    return decks, against_ids


@callback(
    Output('_pages_location', 'search', allow_duplicate=True),
    Input(_decklist_filter_include, 'value'),
    Input(_decklist_filter_exclude, 'value'),
    Input(_decklist_filter_granularity, 'value'),
    Input(_decklist_filter_placement, 'value'),
    Input(_card_selection, 'value'),
    State(_filter_store, 'data'),
    prevent_initial_call=True
)
def update_url_parameters(include, exclude, granularity, placement, selected_card, tf):
    params = tf.copy()
    params_str = components.tour_filter.create_param_string(params)    
    if include is not None:
        params_str += f'&include={include}'
    if exclude is not None:
        params_str += f'&exclude={exclude}'
    if granularity is not None:
        params_str += f'&granularity={granularity}'
    params_str += f'&placement={placement}'
    if selected_card is not None:
        params_str += f'&selected_card={selected_card}'
    return params_str


# Deck analysis callbacks
@callback(
    Output(_deck_title, 'children'),
    Output(_breadcrumbs, 'items'),
    Output(_deck_options_store, 'data'),
    Input(_filter_store, 'data'),
    State(_deck_options_store, 'data')
)
def update_deck_title(tf, current):
    if len(current) > 0:
        raise exceptions.PreventUpdate
    deck = tf['deck']
    decks = utils.data.get_decks(tf)
    deck = urllib.parse.unquote(deck)
    try:
        deck_object = next(d for d in decks if d['id'] == deck)
        label = components.deck_label.format_label(deck_object)
        deck_title = deck_object['name']
    except StopIteration:
        label = f'Deck {deck} not found.'
        deck_title = deck
    return label, create_breadcrumb_items(deck_title, tf), decks


@callback(
    Output(_deck_matchups, 'children'),
    Input(_filter_store, 'data'),
    Input(_deck_options_store, 'data'),
    Input(_decklist_filter_against_archetypes, 'value'),
    background=True
)
def update_deck_matchups(tf, options, against):
    if len(options) == 0:
        raise exceptions.PreventUpdate

    url = f'{utils.data.analysis_url}/decklists/{tf["deck"]}/card-matchups/overall'
    params = tf.copy()
    params['against_archetypes'] = against
    r = utils.data.session.post(url, params=params)
    matchups = []
    if r.status_code == 200:
        matchups = r.json()['data']
    decks = {d['name']: d for d in options}
    current_deck = next(d['name'] for d in options if d['id'] == tf['deck'])
    for m in matchups:
        m['count'] = current_deck
    return components.matchup_table.create_matchup_spread(matchups, decks, player='count', against='deck_other')


def _create_card_inclusion_bar(count, percentage):
    return dbc.Row([
        dbc.Col(
            html.Div(count), xs=1),
        dbc.Col(
            dbc.Progress(value=percentage, max=1,
                            color=utils.colors.blue, label=f'{percentage:.1%}'),
            xs=10)
    ], class_name='mb-1 align-items-center')


@callback(
    Output(_deck_count, 'children'),
    Output(_decklist_skeleton, 'children'),
    Output(_decklist_skeleton_clipboard, 'content'),
    Output(_card_inclusion, 'children'),
    Output(_card_count_inclusion, 'children'),
    Input(_filter_store, 'data'),
    Input(_decklist_skeleton_view_toggle, 'value'),
    background=True
)
def update_skeleton(tf, view):
    url = f'{utils.data.analysis_url}/decklists/{tf["deck"]}/skeleton-counts'
    params = tf.copy()
    if 'include' in tf:
        params['include_card'] = tf['include']
    if 'exclude' in tf:
        params['exclude_card'] = tf['exclude']
    params['granularity'] = tf['granularity']
    r = utils.data.session.post(url, params=params)
    out = {'cards': [], 'total': 0}
    total = out['total']
    if r.status_code == 200:
        resp = r.json()
        out['cards'] = resp['data']
        total = resp['total']

    skeleton = [c for c in out['cards'] if c['skeleton']]
    skeleton_list = '\n'.join((' '.join(str(c[k]) for k in ['count', 'name', 'set', 'number']) for c in skeleton))
    skeleton_layout = components.card_table.container_layout[view](out['cards'], total, tf['game'])
    card_inclusion_text = ''
    card_inclusion_chart = html.Div()
    if tf['selected_card'] is not None:
        card = next((c for c in out['cards'] if c['card_code'] == tf['selected_card']), None)
        if card is None:
            card_inclusion_text = '?%'
        else:
            card_inclusion_text = f"{card['play_rate']:.1%}"
            card_inclusion_bars = [
                _create_card_inclusion_bar(c['count'], c['decks']/total)
                for c in sorted(card['counts'], key=lambda d: d['count'])
            ]
            card_inclusion_chart = html.Div([
                'Card count play rates',
                _create_card_inclusion_bar(0, 1-card['play_rate'])
            ] + card_inclusion_bars)

    return total, skeleton_layout, skeleton_list, card_inclusion_text, card_inclusion_chart


@callback(
    Output(_card_trend, 'children'),
    Input(_filter_store, 'data'),
    background=True
)
def update_card_trend_children(tf):
    if tf['selected_card'] is None:
        return html.Div()
    url = f'{utils.data.analysis_url}/decklists/{tf["deck"]}/trend/{tf["selected_card"]}'
    r = utils.data.session.post(url, params=tf)
    trend = []
    if r.status_code == 200:
        trend = r.json()['data']

    df = pd.DataFrame.from_records(
        trend,
        columns=['date', 'card_count', 'counts', 'percent']
    )

    return components.trend_graph.create_trend_graph(df)


@callback(
    Output(_card_matchups, 'children'),
    Input(_filter_store, 'data'),
    Input(_deck_options_store, 'data'),
    Input(_decklist_filter_against_archetypes, 'value'),
    background=True
)
def update_card_matchups_children(tf, options, against):
    if tf['selected_card'] is None:
        return html.Div()
    
    if len(options) == 0:
        raise exceptions.PreventUpdate
    url = f'{utils.data.analysis_url}/decklists/{tf["deck"]}/card-matchups/{tf["selected_card"]}'
    params = tf.copy()
    params['against_archetypes'] = against
    r = utils.data.session.post(url, params=params)
    matchups = []
    if r.status_code == 200:
        matchups = r.json()['data']

    decks = {d['name']: d for d in options}
    return components.matchup_table.create_matchup_spread(matchups, decks, player='count', against='deck_other', small_view=True)
