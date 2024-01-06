from collections import Counter
import dash
from dash import html, dcc, exceptions, clientside_callback, ClientsideFunction, callback, Output, Input, State, Patch, ALL, ctx, no_update
import dash_bootstrap_components as dbc
import datetime

from components import deck_label, matchup_table
import utils.data

dash.register_page(
    __name__,
    path='/tools/battle-log',
    title='Battle Log',
    image='tools.png',
    description='Track your Pokémon TCG matches with our tool: Record opponents, game outcomes, notes, and more. Download your data for in-depth analysis.'
)

RESULT_COLORS = {'Win': 'success', 'Loss': 'danger', 'Tie': 'warning'}

prefix = 'battle-log'
game_store = f'{prefix}-games-store'
history = f'{prefix}-history'
analysis = f'{prefix}-analysis'
archetype_store = f'{prefix}-archetype-store'

# buttons
download = f'{prefix}-download'
import_id = f'{prefix}-import'
clear_id = f'{prefix}-clear'

# options
options = f'{prefix}-options'
deck_select = f'{options}-deck-select'
opp_select = f'{options}-opp-select'
best_of = f'{options}-best-of'
game = f'{options}-game'
result = f'{options}-result'
turn = f'{options}-turn'
tags = f'{options}-tags'
notes = f'{options}-notes'
submit = f'{options}-submit'

fake_data = [
    {'playing': 'charizard-ex', 'against': 'mew-meloetta', 'time': '2024-01-04 17:01:12.891066', 'result': 'Win', 'game1': {'result': 'Tie', 'turn': 'First', 'tags': None, 'notes': None}},
    {'playing': 'mew-meloetta', 'against': 'charizard-ex', 'time': '2024-01-04 17:01:12.891066', 'result': 'Win', 'game1': {'result': 'Tie', 'turn': 'First', 'tags': None, 'notes': None}},
    {'playing': 'charizard-ex', 'against': 'giratina-lz-box', 'time': '2024-01-04 17:01:12.891066', 'result': 'Loss', 'game1': {'result': 'Loss', 'turn': 'First', 'tags': None, 'notes': None}},
    {'playing': 'charizard-ex', 'against': 'roaring-moon-ex', 'time': '2024-01-04 17:01:40.000867', 'result': 'Tie', 'game1': {'result': 'Win', 'turn': 'Second', 'tags': [], 'notes': ''}, 'game2': {'result': 'Loss', 'turn': 'First', 'tags': [], 'notes': ''}, 'game3': {'result': 'Win', 'turn': 'Second', 'tags': [], 'notes': ''}}
]

def create_options():
    games = [dbc.Col([
        dbc.Card([
            dbc.CardHeader(f'Game {g + 1}'),
            dbc.CardBody([
                dbc.Label('Result*' if g == 0 else 'Result'),
                dbc.RadioItems(id={'type': result, 'index': g}, options=['Win', 'Loss', 'Tie'], inline=True),
                dbc.Label('Turn'),
                dbc.RadioItems(id={'type': turn, 'index': g}, options=['First', 'Second'], inline=True),
                dbc.Label('Tags'),
                dbc.Checklist(id={'type': tags, 'index': g}),
                dbc.Label('Notes'),
                dbc.Textarea(id={'type': notes, 'index': g}),
            ])
        ])
    ], id={'type': game, 'index': g}, lg=4) for g in range(0, 3)]
    add_round = dbc.Form([
        html.H4('Options'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Playing*'),
                dcc.Dropdown(id=deck_select),
            ], class_name='flex-md-grow-1'),
            dbc.Col('VS', md=1, class_name='text-center fw-bolder'),
            dbc.Col([
                dbc.Label('Against*'),
                dcc.Dropdown(id=opp_select),
            ], class_name='flex-md--grow-1'),
        ], align='center'),
        dbc.Label('Number of Games'),
        dbc.RadioItems(id=best_of, options={'1': 'Best of 1', '3': 'Best of 3'}, inline=True, value='1'),
        dbc.Row(games),
        html.Small('* required fields'),
        dbc.Button('Add Game', id=submit, type='submit', class_name='mt-1 float-end'),
    ], class_name='mb-5')
    return add_round


def layout():
    archetypes = utils.data.get_decks({'start_date': datetime.date.today() - datetime.timedelta(21)})
    decks = {d['id']: d for d in archetypes}
    analysis_tab = html.Div(
        dbc.Spinner(id=analysis)
    )
    cont = html.Div([
        html.H2('Battle Log'),
        html.Div([
            # TODO implement these
            # dbc.Button([html.I(className='fas fa-upload me-1'), 'Import'], id=import_id, class_name='me-1'),
            # dbc.Button([html.I(className='fas fa-download me-1'), 'Download'], id=download, class_name='me-1'),
            html.Div(dcc.ConfirmDialogProvider(
                dbc.Button([html.I(className='far fa-trash-can me-1'), 'Clear']),
                id=clear_id,
                message='Are you sure you want to remove your data? This cannot be undone.'
            ), className='d-inline-block')
        ], className='mb-1'),
        dbc.Tabs([
            dbc.Tab(dbc.Spinner(create_options()), label='Add'),
            dbc.Tab(dbc.Row(id=history, class_name='flex-column-reverse'), label='History'),
            dbc.Tab(analysis_tab, label='Analysis')
        ]),
        dcc.Store(id=game_store, data=fake_data, storage_type='session'),
        dcc.Store(id=archetype_store, data=decks)
    ])
    return cont

# general callbacks
clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='clear_history'),
    Output(game_store, 'data', allow_duplicate=True),
    Input(clear_id, 'submit_n_clicks'),
    allow_duplicate=True,
    prevent_initial_call=True
)


@callback(
    Output(deck_select, 'options'),
    Output(opp_select, 'options'),
    Input(archetype_store, 'data')
)
def update_deck_options(decks):
    deck_options = [{'label': deck_label.format_label(d), 'value': d['id']} for d in decks.values()]
    return deck_options, deck_options


# add match callbacks
def determine_match_result(results, num_games):
    if num_games == '1':
        return results[0]
    if 'Tie' in results:
        return 'Tie'
    result_counts = Counter(results)
    wins = result_counts.get('Win', 0)
    losses = result_counts.get('Loss', 0)
    if wins == losses:
        return 'Tie'
    if wins > losses:
        return 'Win'
    return 'Loss'


@callback(
    Output(game_store, 'data'),
    Input(submit, 'n_clicks'),
    State(deck_select, 'value'),
    State(opp_select, 'value'),
    State(best_of, 'value'),
    State({'type': result, 'index': ALL}, 'value'),
    State({'type': turn, 'index': ALL}, 'value'),
    State({'type': tags, 'index': ALL}, 'value'),
    State({'type': notes, 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def add_round(clicks, playing, against, num_games, game_results, game_turns, game_tags, game_notes):
    if clicks is None:
        return exceptions.PreventUpdate

    match_result = determine_match_result(game_results, num_games)
    new_match = {
        'playing': playing,
        'against': against,
        'time': str(datetime.datetime.now()),
        'result': match_result
    }
    for i in range(0, 3):
        if i > 0 and num_games == '1':
            break
        new_match[f'game{i+1}'] = {
            'result': game_results[i],
            'turn': game_turns[i],
            'tags': game_tags[i],
            'notes': game_notes[i]
        }
    patch = Patch()
    patch.append(new_match)
    return patch


clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='disabled_submit'),
    Output(submit, 'disabled'),
    Input(deck_select, 'value'),
    Input(opp_select, 'value'),
    Input({'type': result, 'index': 0}, 'value')
)

clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='toggle_bo1_bo3'),
    Output({'type': game, 'index': ALL}, 'className'),
    Input(best_of, 'value')
)

clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='clear_battle_log_options'),
    Output(opp_select, 'value'),
    Output({'type': result, 'index': ALL}, 'value'),
    Output({'type': turn, 'index': ALL}, 'value'),
    Output({'type': tags, 'index': ALL}, 'value'),
    Output({'type': notes, 'index': ALL}, 'value'),
    Input(submit, 'n_clicks')
)

# history callbacks
def create_game(g, decks):
    matchup = dbc.Row([
        html.Div(deck_label.format_label(decks[g['playing']]), className='d-flex w-auto'),
        html.Div('vs.', className='d-flex w-auto'),
        html.Div(deck_label.format_label(decks[g['against']]), className='d-flex w-auto')
    ], align='center')
    game = dbc.Card([
        matchup
    ], body=True, color=RESULT_COLORS[g['result']], className='bg-opacity-25')
    return game


@callback(
    Output(history, 'children'),
    Input(game_store, 'modified_timestamp'),
    State(game_store, 'data'),
    Input(archetype_store, 'modified_timestamp'),
    State(archetype_store, 'data')
)
def update_history(history_ts, data, archetype_ts, decks):
    if history_ts is None or archetype_ts is None:
        raise exceptions.PreventUpdate
    games = [create_game(g, decks) for g in data]
    return games


# analysis callbacks
def create_deck_breakdown(data, decks):
    breakdown = {}
    overall = {'Win': 0, 'Loss': 0, 'Tie': 0, 'total': 0}
    for m in data:
        m_play = m['playing']
        if m_play not in breakdown:
            breakdown[m_play] = {'Win': 0, 'Loss': 0, 'Tie': 0, 'total': 0}
        breakdown[m_play][m['result']] += 1
        breakdown[m_play]['total'] += 1

        overall[m['result']] += 1
        overall['total'] += 1
    sort_breakdown = dict(sorted(breakdown.items(), key=lambda x: x[1]['total'], reverse=True))
    output = html.Div([
        html.H4('Breakdown'),
        html.Div(f"Overall record: {overall['Win']}-{overall['Loss']}-{overall['Tie']}"),
        html.Div(f"Overall win-rate: {(overall['Win'] / overall['total']):.1%}"),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th('Deck'), html.Th('Record')
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(deck_label.format_label(decks[b])),
                    html.Td(f"{breakdown[b]['Win']}-{breakdown[b]['Loss']}-{breakdown[b]['Tie']}")
                ]) for b in sort_breakdown
            ])
        ])
    ])
    return output


def prep_matchup_spread(data):
    matchup_dict = {}
    for m in data:
        m_play = m['playing']
        m_agai = m['against']
        if m_play not in matchup_dict:
            matchup_dict[m_play] = {}
        if m_agai not in matchup_dict[m_play]:
            matchup_dict[m_play][m_agai] = {'Win': 0, 'Loss': 0, 'Tie': 0}
        matchup_dict[m_play][m_agai][m['result']] += 1

    matchup_list = []
    for m in matchup_dict:
        for a in matchup_dict[m]:
            total = matchup_dict[m][a]['Win'] + matchup_dict[m][a]['Loss'] + matchup_dict[m][a]['Tie']
            matchup_list.append({
                'playing': m,
                'against': a,
                'total': total,
                'win_rate': round(matchup_dict[m][a]['Win'] / total * 100, 1)
            })
    return matchup_list


@callback(
    Output(analysis, 'children'),
    Input(game_store, 'modified_timestamp'),
    State(game_store, 'data'),
    Input(archetype_store, 'modified_timestamp'),
    State(archetype_store, 'data')
)
def update_matchups(history_ts, data, archetype_ts, decks):
    if history_ts is None or archetype_ts is None:
        raise exceptions.PreventUpdate
    if len(data) == 0:
        return dbc.Alert('Please add matches before accessing analysis tools.', color='danger')
    breakdown_data = create_deck_breakdown(data, decks)
    matchup_list = prep_matchup_spread(data)
    matchup_data = html.Div([
        html.H4('Matchups'),
        matchup_table.create_matchup_spread(matchup_list, decks, player='playing', against='against')
    ])
    return html.Div([
        breakdown_data,
        matchup_data
    ])
