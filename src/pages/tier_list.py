import dash
from dash import html, dcc, clientside_callback, ClientsideFunction, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
from datetime import date
import platform

from components import tour_filter, page_too_small, deck_label
import utils.data

dash.register_page(
    __name__,
    path='/tools/tier-list',
    title='Tier List Creator',
    image='tools.png',
    description='Strategically categorize Pokémon TCG deck archetypes with our Tier List tool. Easily create and customize tier lists based on tournament data and personal insights. Ideal for visualizing the competitive landscape and identifying top-performing decks.'
)
date_format = '%B %#d, %G' if platform.system() == 'Windows' else '%B %-d, %G'

prefix = 'tier-list'
report_card = f'{prefix}-list-report'
download_button = f'{prefix}-list-download'
archetype_dropdown = f'{prefix}-archetype-dropdown'
title_input = f'{prefix}-list-title-input'
title_text = f'{prefix}-list-title-text'

date_created = f'{prefix}-list-date-created'

drag_container = f'{prefix}-list-archetype-drag-container'
drag_wrapper = f'{prefix}-list-archetype-drag-wrapper'

archetype_tray = f'{prefix}-list-archetype-tray'


def create_deck_card(deck):
    card = dbc.Col(
        dbc.Card(
            deck['label'],
            outline=True,
            color='dark',
            class_name='deck-card',
        ),
        class_name='flex-grow-0',
        id=deck['value']
    )
    return card


def create_tier_row(tier, color, bottom_border=False, top=False):
    bottom_css = 'rounded-bottom' if bottom_border else 'border-bottom-0'
    top_css = 'rounded-top' if top else ''
    return dbc.Row(
        [
            dbc.Col(html.Div(html.P(tier.upper()), className=f'tier-list-header bg-{color}'), width=1),
            dbc.Col(
                width=11,
                class_name='tier-list-content',
                id={
                    'index': tier,
                    'type': drag_container
                }
            )
        ],
        class_name=f'tier-list-row g-0 {bottom_css} {top_css}',
    )


def layout(players=None, start_date=None, end_date=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, prefix)
    archetype_raw = utils.data.get_decks(tour_filter.create_tour_filter(players, start_date, end_date))

    decks = [{
        'label': deck_label.format_label(deck),
        'value': deck['id'],
        'search': deck['name']
    } for deck in archetype_raw]

    tier_list_tab = dbc.Card(
        html.Div(
            [
                create_tier_row('s', 'red', top=True),
                create_tier_row('a', 'orange'),
                create_tier_row('b', 'yellow'),
                create_tier_row('c', 'teal'),
                create_tier_row('d', 'green', bottom_border=True),
                dbc.Row(
                    html.Small(f'Created on {date.today().strftime(date_format)}')
                ),
                dbc.Spinner(dbc.Row(
                    id={
                        'index': archetype_tray,
                        'type': drag_container
                    },
                    class_name='g-1 pb-1'
                ))
            ],
            id=drag_wrapper
        ),
        id=report_card,
        class_name='mt-1 border-0',
    )
    cont = html.Div([
        page_too_small.alert,
        html.H2('Tier List Creator'),
        dbc.Alert(html.Ul([
            html.Li([html.Strong('Drag n Drop:'), ' Easily create your tier list by dragging and dropping decks into tiers.']),
            html.Li([
                html.Strong('Need assistance?:'), ' If you encounter an issue or have suggestions, please submit a ',
                html.A('Feedback Form', href='/feedback', className='alert-link'), '.'
            ])
        ], className='mb-0'), id='tierlist-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        tours,
        html.Div([
            dbc.Label('Archetype select'),
            dcc.Dropdown(
                id=archetype_dropdown, multi=True,
                options=decks, value=[d['value'] for d in decks][:15], maxHeight=400
            ),
        ], className='mb-1'),
        tier_list_tab
    ])
    return cont


clientside_callback(
    ClientsideFunction(namespace='drag', function_name='make_draggable'),
    Output(drag_wrapper, 'data-drag'),
    Input({'type': drag_container, 'index': ALL}, 'id')
)

@callback(
    Output({'type': drag_container, 'index': archetype_tray}, 'children'),
    Input(archetype_dropdown, 'value'),
    State(archetype_dropdown, 'options')
)
def update_selected_decks(selected, options):
    archetype_cards = [create_deck_card(d) for d in options if d['value'] in selected]
    return archetype_cards
