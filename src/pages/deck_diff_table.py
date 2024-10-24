import dash
from dash import html, callback, Output, Input, State, Patch, ALL
import dash_bootstrap_components as dbc

from components import download_button, feedback_link, deck_select
from utils import images, cards as _cards

# TODO download button, prototype banner, more deck entry methods
# caching limitless stuff

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

def layout():
    cont = html.Div([
        html.Div([
            html.H2([html.I(className=f'fas {page_icon} me-1'), page_title], className='d-inline-block'),
            download_button.DownloadImageAIO(dom_id=card_table, className='float-end')
        ]),
        dbc.Alert(html.Ul([
            html.Li([html.Strong('Quickly compare:'), ' Analyze and compare multiple decklists.']),
            html.Li([html.Strong('Decklist input:'), ' Select decks from LimitlessTCG or input decks manually to compare.']),
            feedback_link.list_item,
        ], className='mb-0'), id='tour-meta-report-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        html.Div([deck_select.DeckSelectAIO(aio_id=0)], id=deck_selection_table),
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
    patch.append(deck_select.DeckSelectAIO(aio_id=clicks, event=last_event))
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
            id = f'{card["set"]}-{card["number"]}'
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
        fetched_card = _cards.get_card(card)
        fetched_card['decks'] = deck_counts
        card_info.append(fetched_card)
    sorted_cards = _cards.sort_deck(card_info)

    headers = [html.Th('')]
    for label in labels:
        headers.append(html.Th(html.Div(html.Div(label))))
    rows = []
    for card in sorted_cards:
        card_id = f"{card['set']}-{card['number'].zfill(3)}"
        cells = [html.Td([
            dbc.Popover(
                dbc.PopoverBody(
                    html.Img(src=images.get_card_image(card_id, 'SM'), className='w-100')
                ), target=card_id, trigger='hover legacy', placement='bottom'
            ),
            card['name']
        ], id=card_id)]

        for _ in decks:
            cells.append(html.Td(''))
        for item in card['decks']:
            color = 'success' if item[1] > card['count'] else 'danger' if item[1] < card['count'] else ''
            diff = abs(item[1] - card['count'])
            opacity = '25' if diff >= 2 else '50' if diff >= 1 else '75'
            cells[item[0]+1] = html.Td(item[1], className=f'bg-opacity-{opacity} bg-{color} text-center')

        if hide and len(card['decks']) == len(decks) and all(c[1] == card['decks'][0][1] for c in card['decks']):
            continue
        rows.append(html.Tr(cells))
    table_children = [html.Thead(headers, className='sticky-top')] + [html.Tbody(rows)]
    return table_children
