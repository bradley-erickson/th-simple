import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import math

from components import tour_filter, deck_label
from utils import colors, data

dash.register_page(
    __name__,
    path='/decklist',
    redirect_from=['/analysis/decklist'],
    title='Decklist Analysis',
    description=''
)

prefix = 'deck-select'
tour_store = f'{prefix}-tour-store'
table = f'{prefix}-table'

def layout(players=None, start_date=None, end_date=None, platform=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, platform, prefix)
    tour_filters = tour_filter.create_tour_filter(players, start_date, end_date, platform)
    cont = html.Div([
        html.H2('Decklist Analysis'),
        tours,
        dcc.Store(id=tour_store, data=tour_filters),
        html.H3('Deck Select'),
        dbc.Spinner(dbc.Table(id=table))
    ])
    return cont

@callback(
    Output(table, 'children'),
    Input(tour_store, 'data')
)
def update_table(tf):
    decks_raw = data.get_decks(tf)
    params = tour_filter.create_param_string(tf)
    body = html.Tbody([
        html.Tr([
            html.Td(f'{i+1}.'),
            html.Td(
                html.A(
                    deck_label.format_label(deck),
                    href=f'/decklist/{deck["id"]}{params}'
                )
            )
        ], className='deck-row') for i, deck in enumerate(decks_raw[:50])
    ])
    return body
