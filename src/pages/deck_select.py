import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import math

from components import tour_filter, deck_label
from utils import colors, data, cache

dash.register_page(
    __name__,
    path='/decklist',
    redirect_from=['/analysis/decklist'],
    title='Decklist Analysis',
    description=''
)

prefix = 'deck-select'
tour_store = f'{prefix}-tour-store'
_search = f'{prefix}-search'
table = f'{prefix}-table'

def layout(players=None, start_date=None, end_date=None, platform=None, game=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, platform, game, prefix)
    tour_filters = tour_filter.create_tour_filter(players, start_date, end_date, platform, game)
    cont = html.Div([
        html.H2('Decklist Analysis'),
        tours,
        dcc.Store(id=tour_store, data=tour_filters),
        html.H3('Deck Select'),
        dbc.Input(placeholder='Search for a deck', id=_search, class_name='mb-1'),
        dbc.Spinner(dbc.Table(id=table))
    ])
    return cont


@cache.cache.memoize(86400)
def _fetch_decks(tf):
    return data.get_decks(tf)


@callback(
    Output(table, 'children'),
    Input(tour_store, 'data'),
    Input(_search, 'value')
)
def update_table(tf, search):
    decks_raw = _fetch_decks(tf)
    params = tour_filter.create_param_string(tf)
    body = html.Tbody([
        html.Tr([
            html.Td(f'{i+1}.'),
            html.Td(
                dcc.Link(
                    deck_label.format_label(deck),
                    href=f'/decklist/{deck["id"]}{params}'
                )
            )
        ], className='deck-row' if not search or search.strip().lower() in deck.get('name', '').lower() else 'd-none')
        for i, deck in enumerate(decks_raw[:50])
    ])
    return body
