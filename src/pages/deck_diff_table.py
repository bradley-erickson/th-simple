import dash
from dash import html, callback, Output, Input, State, Patch, ALL, ctx
import dash_bootstrap_components as dbc

from components import download_button, feedback_link, deck_select, help_icon
import utils.cards
import utils.decklists
import utils.images

page_title = 'Deck Diff Table Compare'
page_icon = 'fa-table'

dash.register_page(
    __name__,
    path='/tools/deck-diff-table',
    title=page_title,
    image='tools.png',
    icon=page_icon,
    description='Compare and contrast multiple Pokémon TCG decklists with our Deck Diff tool. Generate intuitive Venn diagrams to visualize card overlaps and differences, helping you refine your deck choices and understand key strategic variations.'
)

prefix = 'deck-diff-table'
deck_selection_table = f'{prefix}-deck-selection'
add_row = f'{prefix}-add-row-btn'
card_table = f'{prefix}-card-table'
hide_common = f'{prefix}-hide-common'
_remove_item = f'{prefix}-remove-item'

_helper_progress_bar = [dbc.Progress(value=14, color='danger', bar=True, class_name=f'bg-opacity-{o}') for o in [75, 50, 25]] +\
    [dbc.Progress(value=16, color='transparent', bar=True)] +\
    [dbc.Progress(value=14, color='success', bar=True, class_name=f'bg-opacity-{o}') for o in [25, 50, 75]]

_help_icon = f'{prefix}-help'
_help_children = html.Ul([
    html.Li([html.Strong('Quickly compare:'), ' Analyze and compare multiple decklists.']),
    html.Li([html.Strong('Decklist input:'), ' Select decks from LimitlessTCG or input decks manually to compare.']),
    html.Li([
        html.Strong('Color-coded insights:'), ' Understand how a card count compares to the average',
        dbc.Progress(_helper_progress_bar),
        html.Div([dbc.Label('<<'), dbc.Label('<'), dbc.Label('='), dbc.Label('>'), dbc.Label('>>')], className='d-flex justify-content-between')
    ]),
    feedback_link.list_item,
], className='mb-0')


def create_decklist_row(id, event=None):
    return dbc.Spinner(html.Div([
        deck_select.DeckSelectAIO(aio_id=id, event=event, className='d-flex flex-grow-1'),
        html.Div(dbc.Button(
            html.I(className='fas fa-trash text-primary'),
            id={'type': _remove_item, 'index': id},
            title='Remove deck',
            color='transparent',
        ), className='ms-3'),
    ], id=f'decklist-{id}', className='d-flex'))


def layout():
    cont = html.Div([
        html.Div([
            html.H2([html.I(className=f'fas {page_icon} me-1'), page_title], className='d-inline-block'),
            help_icon.create_help_icon(_help_icon, _help_children, className='align-top'),
            download_button.DownloadImageAIO(dom_id=card_table, className='float-end')
        ]),
        dbc.Alert(_help_children, id='tour-meta-report-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        html.Div([create_decklist_row(0)], id=deck_selection_table),
        dbc.Button([html.I(className='fas fa-plus me-1'), 'Add'], id=add_row),
        dbc.Checkbox(id=hide_common, value=False, label='Hide common cards'),
        dbc.Spinner(dbc.Table(id=card_table, bordered=True))
    ])
    return cont


@callback(
    Output(deck_selection_table, 'children'),
    Input(add_row, 'n_clicks'),
    State(deck_select.DeckSelectAIO.ids.limitless_events(ALL), 'value')
)
def add_row_to_table(clicks, curr_events):
    if not clicks:
        raise dash.exceptions.PreventUpdate
    patch = Patch()
    last_event = curr_events[-1] if len(curr_events) > 0 else None
    patch.append(create_decklist_row(id=clicks, event=last_event))
    return patch


@callback(
    Output(deck_selection_table, 'children', allow_duplicate=True),
    Input({'type': _remove_item, 'index': ALL}, 'n_clicks'),
    State(deck_selection_table, 'children'),
    prevent_initial_call=True
)
def remove_row_from_table(clicks, children):
    triggered_id = ctx.triggered_id.get('index', None)
    if triggered_id is None:
        raise dash.exceptions.PreventUpdate
    matched_idx = next(idx for idx, child in enumerate(children) if f'decklist-{triggered_id}' == child['props']['children']['props'].get('id', None))
    if clicks[matched_idx] is None:
        raise dash.exceptions.PreventUpdate
    patch = Patch()
    del patch[matched_idx]
    return patch


@callback(
    Output(card_table, 'children'),
    Input(deck_select.DeckSelectAIO.ids.decklist(ALL), 'data'),
    Input(deck_select.DeckSelectAIO.ids.label(ALL), 'children'),
    Input(hide_common, 'value')
)
def update_card_table(decks, labels, hide):
    cards = {}
    for i, deck in enumerate(decks):
        if deck is None: continue
        for card in deck:
            id = card['unique']
            if id not in cards:
                cards[id] = card
                cards[id]['decks'] = []
            cards[id]['decks'].append((i, card['count']))
    for card in cards:
        counts = [c[1] for c in cards[card]['decks']]
        cards[card]['count'] = sum(counts) / len(decks)
    card_info = []
    for card in cards.values():
        deck_counts = card['decks']
        fetched_card = utils.cards.get_card(card)
        fetched_card['decks'] = deck_counts
        card_info.append(fetched_card)
    sorted_cards = utils.cards.sort_deck(card_info)

    headers = [html.Th('')]
    for label in labels:
        headers.append(html.Th(html.Div(html.Div(label))))
    rows = []
    for card in sorted_cards:
        card_id = f"{card['set']}-{card['number'].zfill(3)}"
        cells = [html.Td([
            dbc.Popover(
                dbc.PopoverBody(
                    html.Img(src=utils.images.get_card_image(card_id, 'SM'), className='w-100')
                ), target=card_id, trigger='hover legacy', placement='bottom'
            ),
            card['name']
        ], id=card_id)]

        for _ in decks:
            cells.append(html.Td(''))
        for item in card['decks']:
            color = 'success' if item[1] > card['count'] else 'danger' if item[1] < card['count'] else ''
            diff = abs(item[1] - card['count'])
            opacity = '75' if diff >= 2 else '50' if diff >= 1 else '25'
            cells[item[0]+1] = html.Td(item[1], className=f'bg-opacity-{opacity} bg-{color} text-center')

        if hide and len(card['decks']) == len(decks) and all(c[1] == card['decks'][0][1] for c in card['decks']):
            continue
        rows.append(html.Tr(cells))
    table_children = [html.Thead(headers, className='sticky-top')] + [html.Tbody(rows)]
    return table_children
