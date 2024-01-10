from dash import html
import dash_bootstrap_components as dbc
import math

from components import deck_label
from utils import colors

def create_record_string(match):
    if 'Win' in match and 'Loss' in match:
        tied = f'-{match["Tie"]}' if 'Tie' in match else ''
        record_string = f'{match["Win"]}-{match["Loss"]}{tied}'
        return record_string
    if 'wins' in match and 'losses' in match:
        tied = f'-{match["ties"]}' if 'ties' in match else ''
        record_string = f'{match["wins"]}-{match["losses"]}{tied}'
        return record_string
    return None


def create_matchup_tile(match, decks, player, against):
    if match is None or math.isnan(match['win_rate']):
        return html.Td('-', className='text-center align-middle')
    id = match[player] + match[against]
    wr = match['win_rate']
    record = create_record_string(match)
    color = colors.win_rate_color_bar[math.floor(wr)][1]
    vs_item = html.Div([
        html.Span(deck_label.format_label(decks[match[player]], hide_text=True)),
        html.Span('vs.', className='mx-2'),
        html.Span(deck_label.format_label(decks[match[against]], hide_text=True)),
    ], className='d-flex align-items-center')
    return html.Td([
        html.Div([wr, html.Div(record)], id=id, className='text-center'),
        dbc.Popover(
            dbc.PopoverBody([
                vs_item,
                html.Div(f'{wr}%'),
                html.Div(record)
            ], class_name='text-dark text-center'),
            style={'backgroundColor': color},
            target=id,
            trigger='hover',
            placement='bottom'
        ),
    ], style={'backgroundColor': color, 'width': '112px'}, className='text-center text-dark align-middle')

def create_matchup_table_row(deck, data, decks, player, against):
    matches = [create_matchup_tile(match, decks, player, against) for match in data]
    row = html.Tr([html.Td(deck_label.format_label(decks[deck]), className='text-nowrap align-middle')] + matches)
    return row

def create_matchup_tile_full(match, decks, player, against):
    if match is None or math.isnan(match['win_rate']):
        return html.Span()
    id = match[player] + match[against]
    wr = match['win_rate']
    record = create_record_string(match)
    color = colors.win_rate_color_bar[math.floor(wr)][1]
    vs_item = html.Div([
        html.Span('vs.', className='me-1'),
        html.Span(deck_label.format_label(decks[match[against]], hide_text=True)),
    ], className='d-flex align-items-center')
    return dbc.Card(
        dbc.CardBody([
            vs_item,
            html.Div(f'{match["win_rate"]}%'),
            html.Div(record)
        ], class_name='text-dark text-center p-1'),
        style={'backgroundColor': color},
        className='w-auto',
        id=id
    )    

def create_matchup_tile_row(deck, data, decks, player, against):
    row = html.Div([
        html.H5(deck_label.format_label(decks[deck])),
        dbc.Row([create_matchup_tile_full(match, decks, player, against) for match in data], class_name='g-1')
    ], className='mb-2')
    return row

def create_matchup_spread(data, decks, player='deck1', against='deck2'):
    # Extract unique decks from player and sort them alphabetically
    player_unique_decks = list(set(matchup[player] for matchup in data))
    if len(player_unique_decks) == 0:
        return 'No matchup information found.'
    if 'Plays:' in player_unique_decks[0]:
        player_unique_decks = sorted(player_unique_decks, key=lambda x: int(x.split(':')[1].strip()))
    against_unique_decks = sorted(set(matchup[against] for matchup in data))

    rows = []
    small_rows = []
    # Organize the data
    for deck in player_unique_decks:
        if deck not in decks:
            decks[deck] = {'name': deck}
        matchups = sorted(
            (matchup for matchup in data if matchup[player] == deck),
            key=lambda x: x[against]
        )
        duplicates = [index for index, d in enumerate(matchups) if d[player] == d[against]]
        if len(duplicates) > 1:
            matchups.pop(duplicates[0])

        ordered_matchups = [None for _ in range(len(against_unique_decks))]
        for m in matchups:
            ordered_matchups[against_unique_decks.index(m[against])] = m
        rows.append(create_matchup_table_row(deck, ordered_matchups, decks, player, against))
        small_rows.append(create_matchup_tile_row(deck, ordered_matchups, decks, player, against))
    
    header_labels = [
        html.Div(deck_label.format_label(decks[deck], hide_text=True), className='d-flex justify-content-center')
        for deck in against_unique_decks
    ]
    headers = html.Thead(html.Tr([
        html.Th(deck) for deck in [''] + header_labels
    ]))
    table = dbc.Table([
        headers,
        html.Tbody(rows)
    ], className='d-none d-lg-block')

    small_view = html.Div([
        html.Div(small_rows)
    ], className='d-lg-none')
    return html.Div([table, small_view])
