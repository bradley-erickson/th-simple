import dash
from dash import html, dcc, clientside_callback, ClientsideFunction, callback, Output, Input, State, ALL, Patch
import dash_bootstrap_components as dbc
from datetime import date
import platform

from components import tour_filter, page_too_small, deck_label, download_button, archetype_builder
import utils.data

dash.register_page(
    __name__,
    path='/tools/tier-list',
    title='Tier List Creator',
    image='tools.png',
    icon='fa-ranking-star',
    description='Strategically categorize Pokémon TCG deck archetypes with our Tier List tool. Easily create and customize tier lists based on tournament data and personal insights. Ideal for visualizing the competitive landscape and identifying top-performing decks.'
)
date_format = '%B %#d, %G' if platform.system() == 'Windows' else '%B %-d, %G'

prefix = 'tier-list'
report_card = f'{prefix}-list-report'
additional_archetypes = f'{prefix}-archetype-additional'
archetype_collapse = f'{prefix}-archetype-collapse'
custom_archetypes = f'{prefix}-archetype-custom'
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


def layout(players=None, start_date=None, end_date=None, platform=None):
    tours = tour_filter.TourFiltersAIO(players, start_date, end_date, platform, prefix)
    archetype_raw = utils.data.get_decks(tour_filter.create_tour_filter(players, start_date, end_date, platform))

    decks = [{
        'label': deck_label.format_label(deck),
        'value': deck['id'],
        'search': deck['name']
    } for deck in archetype_raw]


    additional_decks = dbc.Card([
        html.A(
            dbc.CardHeader([
                html.I(className='fas fa-filter me-1'),
                'Custom Deck Archetypes'
            ]),
            id=additional_archetypes
        ),
        dbc.Collapse(
            dbc.CardBody([
                archetype_builder.builder_plus_built(custom_archetypes, other=[d['value'] for d in decks], persistance='session')
            ]),
            id=archetype_collapse
        )
    ])

    tier_list_tab = html.Div([
        dbc.Card(html.Div([
            create_tier_row('s', 'red', top=True),
            create_tier_row('a', 'orange'),
            create_tier_row('b', 'yellow'),
            create_tier_row('c', 'teal'),
            create_tier_row('d', 'green', bottom_border=True),
        dbc.Row(html.Small(f'Created on {date.today().strftime(date_format)}', className='ms-1')),
        ]), id=report_card),
        dbc.Spinner(dbc.Row(
            id={
                'index': archetype_tray,
                'type': drag_container
            },
            class_name='g-1 pb-1'
        ))
    ], id=drag_wrapper)
    cont = html.Div([
        page_too_small.alert,
        html.Div([
            html.H2('Tier List Creator', className='d-inline-block'),
            download_button.DownloadImageAIO(report_card, className='float-end'),
        ]),
        dbc.Alert(html.Ul([
            html.Li([html.Strong('Drag n Drop:'), ' Easily create your tier list by dragging and dropping decks into tiers.']),
            html.Li([
                html.Strong('Need Assistance:'), ' If you encounter an issue or have suggestions, please submit a ',
                html.A('Feedback Form', href='/feedback', className='alert-link'), '.'
            ])
        ], className='mb-0'), id='tierlist-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        tours,
        additional_decks,
        html.Div([
            dbc.Label('Archetype select'),
            dcc.Dropdown(
                id=archetype_dropdown, multi=True,
                options=decks, value=[d['value'] for d in decks if d['value'] != 'other'][:15], maxHeight=400
            ),
            html.Small('* Removing selected decks already placed in a tier may cause the page to crash.')
        ], className='mb-1'),
        tier_list_tab
    ])
    return cont


clientside_callback(
    ClientsideFunction(namespace='drag', function_name='make_draggable'),
    Output(drag_wrapper, 'data-drag'),
    Input({'type': drag_container, 'index': ALL}, 'id')
)

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(archetype_collapse, 'is_open'),
    Input(additional_archetypes, 'n_clicks'),
    State(archetype_collapse, 'is_open')
)

archetype_builder.register_callbacks(custom_archetypes)

@callback(
    Output(archetype_dropdown, 'value'),
    Output(archetype_dropdown, 'options'),
    Input(archetype_builder.ArchetypeBuilderAIO.ids.store(custom_archetypes), 'data'),
    State(archetype_dropdown, 'value'),
    State(archetype_dropdown, 'options'),
)
def add_new_archetypes_to_dropdown(data, curr_val, curr_opt):
    p_val = Patch()
    p_opt = Patch()
    all_ids = [d['value'] for d in curr_opt]
    new_ids = [d['id'] for d in data]
    curr_custom = [d for d in curr_opt if d.get('title', '').startswith('custom')]
    for c in curr_custom:
        if c['value'] not in new_ids:
            p_opt.remove(c)
            if c['value'] in curr_val:
                p_val.remove(c['value'])
    new_decks = [{
        'label': deck_label.format_label(deck),
        'value': deck['id'],
        'search': deck['name'],
        'title': f'custom {deck["name"]}'
    } for deck in data if deck['id'] not in all_ids]
    new_values = [d['value'] for d in new_decks]
    if len(new_decks) > 0 and len(new_values) > 0:
        p_val.prepend(new_values[0])
        p_opt.prepend(new_decks[0])
    return p_val, p_opt


@callback(
    Output({'type': drag_container, 'index': archetype_tray}, 'children'),
    Input(archetype_dropdown, 'value'),
    State(archetype_dropdown, 'options')
)
def update_selected_decks(selected, options):
    archetype_cards = [create_deck_card(d) for d in options if d['value'] in selected]
    return archetype_cards
