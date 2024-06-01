import dash
from dash import html, dcc, clientside_callback, ClientsideFunction, callback, Output, Input, State, ALL, Patch
import dash_bootstrap_components as dbc
from datetime import date
import platform

from components import (tour_filter, page_too_small, deck_label,
                        download_button, archetype_builder, feedback_link,
                        breakdown
)
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

tiers_container = f'{prefix}-tier-container'
archetype_tray = f'{prefix}-list-archetype-tray'

meta_percentage_toggle = f'{prefix}-meta-percentage-toggle'
meta_percentage_input = f'{prefix}-meta-percentage-input'
meta_percentage_breakdown = f'{prefix}-meta-percentage-breakdown'


def create_deck_card(deck):
    card = dbc.Col(
        dbc.Card(html.Span([
                deck['label'],
                dbc.Input(
                    type='number', style={'width': '60px', 'margin-left': '0.25rem'},
                    size='sm', min=0,
                    id={'type': meta_percentage_input, 'index': deck['value']}
                )
            ]),
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
        'search': deck['name'],
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
        dbc.Card([
            dbc.Row([
                dbc.Col([
                    create_tier_row('s', 'red', top=True),
                    create_tier_row('a', 'orange'),
                    create_tier_row('b', 'yellow'),
                    create_tier_row('c', 'teal'),
                    create_tier_row('d', 'green', bottom_border=True),
                ], id=tiers_container, lg=6, xl=8),
                dbc.Col(id=meta_percentage_breakdown, lg=6, xl=4)
            ]),
            dbc.Row(html.Small(f'Created on {date.today().strftime(date_format)}', className='ms-1')),
        ], id=report_card),
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
            feedback_link.list_item
        ], className='mb-0'), id='tierlist-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        tours,
        additional_decks,
        html.Div([
            dbc.Label('Archetype select'),
            dcc.Dropdown(
                id=archetype_dropdown, multi=True,
                options=decks, value=[d['value'] for d in decks if d['value'] != 'other'][:15], maxHeight=400
            ),
            html.Small('* Removing selected decks already placed in a tier may cause the page to crash.'),
            dbc.Switch(label='Show/Hide meta share input (beta)', value=False, id=meta_percentage_toggle),
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

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='show_hide_all_items'),
    Output({'type': meta_percentage_input, 'index': ALL}, 'class_name'),
    Input(meta_percentage_toggle, 'value'),
    State({'type': meta_percentage_input, 'index': ALL}, 'class_name')
)
clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_tier_list_meta_share'),
    Output(tiers_container, 'class_name'),
    Output(meta_percentage_breakdown, 'class_name'),
    Input(meta_percentage_toggle, 'value'),
)

archetype_builder.register_callbacks(custom_archetypes)

@callback(
    Output(archetype_dropdown, 'value'),
    Output(archetype_dropdown, 'options'),
    Input(archetype_builder.ArchetypeBuilderAIO.ids.store(custom_archetypes), 'modified_timestamp'),
    State(archetype_builder.ArchetypeBuilderAIO.ids.store(custom_archetypes), 'data'),
    State(archetype_dropdown, 'value'),
    State(archetype_dropdown, 'options'),
)
def add_new_archetypes_to_dropdown(ts, data, curr_val, curr_opt):
    if ts is None:
        raise dash.exceptions.PreventUpdate
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
        for val, deck in zip(new_values, new_decks):
            p_val.append(val)
            p_opt.append(deck)
    return p_val, p_opt


@callback(
    Output({'type': drag_container, 'index': archetype_tray}, 'children'),
    Input(archetype_dropdown, 'value'),
    State(archetype_dropdown, 'options')
)
def update_selected_decks(selected, options):
    archetype_cards = [create_deck_card(d) for d in options if d['value'] in selected]
    return archetype_cards


@callback(
    Output(meta_percentage_breakdown, 'children'),
    Input({'type': meta_percentage_input, 'index': ALL}, 'value'),
    State(archetype_dropdown, 'options'),
    State({'type': meta_percentage_input, 'index': ALL}, 'id'),
)
def update_meta_breakdown(meta_shares, decks, ids):
    data = []
    for id, val in zip(ids, meta_shares):
        if val is None:
            continue
        data.append({
            'label': next(d['label'] for d in decks if d['value'] == id['index']),
            'percent': val/100
        })

    data = sorted(data, key=lambda x: x['percent'], reverse=True)
    output = [
        html.H4('Meta % Predictions'),
        breakdown.create_ordered_list(data)
    ]
    return output
