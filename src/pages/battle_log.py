import base64
from collections import Counter
import dash
from dash import html, dcc, exceptions, clientside_callback, ClientsideFunction, callback, Output, Input, State, Patch, ALL, ctx, no_update
import dash_bootstrap_components as dbc
import datetime
import io
import numpy as np
import pandas as pd

from components import deck_label, matchup_table, ternary_switch
import utils.data

dash.register_page(
    __name__,
    path='/tools/battle-log',
    title='Battle Log',
    image='tools.png',
    description='Track your Pokémon TCG matches with our tool: Record opponents, game outcomes, notes, and more. Download your data for in-depth analysis.'
)

RESULT_COLORS = {'Win': 'success', 'Loss': 'danger', 'Tie': 'warning'}
TAG_OPTIONS = ['Ahead early', 'Behind early', 'Slow start', 'Lucky', 'Got donked', 'Donked opp', 'Quick game', 'Dead drew', 'Poor prizes']
TAG_OPTIONS_IDS = [t.lower().replace(' ', '_') for t in TAG_OPTIONS]

prefix = 'battle-log'
game_store = f'{prefix}-games-store'
history = f'{prefix}-history'
analysis = f'{prefix}-analysis'
archetype_store = f'{prefix}-archetype-store'

# buttons
download_btn = f'{prefix}-download-button'
download_comp = f'{prefix}-download-component'
upload_id = f'{prefix}-import'
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

# filters
analysis_filter_header = f'{analysis}-filter-header'
analysis_filter_collapse = f'{analysis}-filter-collapse'
analysis_decompose_switch = f'{analysis}-filter-decompose-switch'
analysis_decompose_collapse = f'{analysis}-filter-decompose-collapse'
turn_option = f'{analysis}-filter-turn-switch'


def create_options():
    games = [dbc.Col([
        dbc.Card([
            dbc.CardHeader(f'Game {g + 1}'),
            dbc.CardBody([
                dbc.Label('Result*' if g == 0 else 'Result'),
                dbc.RadioItems(id={'type': result, 'index': g}, options=['Win', 'Loss', 'Tie'], inline=True),
                dbc.Label('Turn'),
                dbc.RadioItems(id={'type': turn, 'index': g}, options={1: 'First', 2: 'Second'}, inline=True, value=0),
                dbc.Label('Tags'),
                dbc.Checklist(id={'type': tags, 'index': g}, inline=True, options=TAG_OPTIONS, value=[]),
                dbc.Label('Notes'),
                dbc.Textarea(id={'type': notes, 'index': g}, maxlength=300),
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


tag_filters = [ternary_switch.create_ternary_switch(t_id, t) for t, t_id in zip(TAG_OPTIONS, TAG_OPTIONS_IDS)]
tag_filters.insert(0, ternary_switch.create_ternary_switch(turn_option, 'Turn', options=ternary_switch.TURN_OPTIONS))
analysis_filter_component = dbc.Row([
    dbc.Col(_filter, md=6, lg=4, xl=3) for _filter in tag_filters
])

def layout():
    analysis_tab = html.Div([
        dbc.Card([
            html.A(
                dbc.CardHeader([
                    html.I(className='fas fa-filter me-1'),
                    'Game Filters'
                ]),
                id=analysis_filter_header
            ),
            dbc.Collapse(dbc.CardBody([
                dbc.Switch(label='Decompose Best of 3s', id=analysis_decompose_switch),
                dbc.Collapse(analysis_filter_component, id=analysis_decompose_collapse)
            ]), id=analysis_filter_collapse)
        ]),
        dbc.Spinner(id=analysis)
    ])
    fake_data = [
        {'playing': 'other', 'against': 'other', 'time': str(datetime.datetime.now()), 'result': 'Win', 'game1': {'result': 'Win', 'turn': 1, 'tags': ['Lucky', 'Slow start'], 'notes': 'Got off to a rocky start from judge, but we top decked the out.'}},
    ]
    cont = html.Div([
        html.H2('Battle Log'),
        html.Div([
            # TODO finish implementing this
            # html.Span(dcc.Upload(
            #     dbc.Button([html.I(className='fas fa-upload me-1'), 'Upload']),
            #     id=upload_id, multiple=True
            # ), className='d-inline-block me-1'),
            dbc.Button([html.I(className='fas fa-download me-1'), 'Download'], id=download_btn, class_name='me-1'),
            dcc.Download(id=download_comp),
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
        ], className='mb-1'),
        dcc.Store(id=game_store, data=fake_data, storage_type='session'),
        dcc.Store(id=archetype_store, data={})
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

clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='disable_download'),
    Output(download_btn, 'disabled'),
    Input(game_store, 'data')
)


def parse_file_content(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return []
    print(df.head())
    return []


# @callback(
#     Output(game_store, 'data', allow_duplicate=True),
#     Input(upload_id, 'contents'),
#     State(upload_id, 'filename'),
#     prevent_initial_call=True
# )
# def upload_files(list_of_contents, list_of_filenames):
#     if list_of_contents is None:
#         raise exceptions.PreventUpdate
#     extended_data = []
#     for c, f in zip(list_of_contents, list_of_filenames):
#         extended_data.extend(parse_file_content(c, f))
#     patch = Patch()
#     patch.extend(extended_data)
#     return patch


@callback(
    Output(archetype_store, 'data'),
    Input(game_store, 'modified_timestamp'),
    State(game_store, 'data'),
    State(archetype_store, 'data')
)
def update_archetype_store(ts, data, current):
    if ts is None or len(current) > 0:
        raise exceptions.PreventUpdate
    today = datetime.date.today()
    weeks_ago_3 = str(today - datetime.timedelta(21))
    min_game = min(d['time'] for d in data).split(' ')[0] if len(data) > 0 else str(today)
    start_date = min(min_game, weeks_ago_3)
    archetypes = utils.data.get_decks({'start_date': start_date})
    decks = {d['id']: d for d in archetypes}
    return decks


@callback(
    Output(download_comp, 'data'),
    Input(download_btn, 'n_clicks'),
    State(game_store, 'data')
)
def download_data(clicks, data):
    if clicks is None:
        raise exceptions.PreventUpdate
    df = pd.json_normalize(data, sep='_')
    df.replace(np.nan, None, inplace=True)
    clean_tags = lambda x: '+'.join(x) if x is not None and len(x) > 0 else ''
    df['game1_tags'] = df['game1_tags'].apply(clean_tags)
    if 'game2_tags' in df.columns:
        df['game2_tags'] = df['game2_tags'].apply(clean_tags)
    if 'game3_tags' in df.columns:
        df['game3_tags'] = df['game3_tags'].apply(clean_tags)
    return dcc.send_data_frame(df.to_csv, f'trainerhill-battle-log-{str(datetime.date.today())}.csv', index=False)


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
def create_game(g, title):
    gtags = g['tags']
    gturn = int(g['turn'])
    gnote = g['notes']
    turn_text = f'went {gturn}{"st" if gturn == 1 else "nd"}' if gturn > 0 else ''
    return html.Div([
        f'{title} - {turn_text}',
        html.Span([dbc.Badge(t, color='primary', pill=True, class_name='ms-1') for t in gtags] if gtags is not None else []),
        html.P(gnote if gnote is not None else '')
    ])


def create_match(g, decks):
    matchup = dbc.Row([
        html.Div(deck_label.format_label(decks[g['playing']], hide_text_small=True), className='d-flex w-auto'),
        html.Div('vs.', className='d-flex w-auto'),
        html.Div(deck_label.format_label(decks[g['against']], hide_text_small=True), className='d-flex w-auto')
    ], align='center')
    games = html.Div([
        html.Div([
            create_game(g[f'game{i+1}'], f'Game {i+1}')
        ]) for i in range(3) if g.get(f'game{i+1}', False)
    ])
    match = dbc.Card([
        matchup,
        games
    ], body=True, color=RESULT_COLORS[g['result']], className='bg-opacity-25')
    return match


@callback(
    Output(history, 'children'),
    Input(game_store, 'modified_timestamp'),
    State(game_store, 'data'),
    Input(archetype_store, 'modified_timestamp'),
    State(archetype_store, 'data')
)
def update_history(history_ts, data, archetype_ts, decks):
    if history_ts is None or archetype_ts is None or len(decks) == 0:
        raise exceptions.PreventUpdate
    games = [create_match(g, decks) for g in data]
    return games


# analysis callbacks
clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(analysis_filter_collapse, 'is_open'),
    Input(analysis_filter_header, 'n_clicks'),
    State(analysis_filter_collapse, 'is_open')
)

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='return_self'),
    Output(analysis_decompose_collapse, 'is_open'),
    Input(analysis_decompose_switch, 'value')
)


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


def handle_decompose(data, turn, tags):
    included = set([t for t, t_val in zip(TAG_OPTIONS, tags) if t_val == 1])
    excluded = set([t for t, t_val in zip(TAG_OPTIONS, tags) if t_val == -1])
    decomposed_data = []
    for d in data:
        # handle the filtering
        for i in range(3):
            new_g = {
                'playing': d['playing'],
                'against': d['against'],
                'result': d.get(f'game{i+1}', {}).get('result', None),
                'turn': d.get(f'game{i+1}', {}).get('turn', 0),
                'tags': d.get(f'game{i+1}', {}).get('tags', [])
            }
            if new_g['result'] is None:
                continue
            if turn != 0 and (int(new_g['turn']) if new_g['turn'] is not None else 0) != turn:
                continue
            tag_set = set(new_g['tags'] if new_g['tags'] is not None else [])
            if len(set.intersection(tag_set, excluded)) > 0:
                continue
            if len(included) > 0 and len(set.intersection(tag_set, included)) == 0:
                continue
            decomposed_data.append(new_g)
    return decomposed_data


@callback(
    Output(analysis, 'children'),
    Input(game_store, 'modified_timestamp'),
    State(game_store, 'data'),
    Input(archetype_store, 'modified_timestamp'),
    State(archetype_store, 'data'),
    Input(analysis_decompose_switch, 'value'),
    Input(turn_option, 'value'),
    *[Input(t_id, 'value') for t_id in TAG_OPTIONS_IDS]
)
def update_matchups(history_ts, data, archetype_ts, decks, decompose, turn, *tags):
    if history_ts is None or archetype_ts is None or len(decks) == 0:
        raise exceptions.PreventUpdate
    if len(data) == 0:
        return dbc.Alert('Please add matches before accessing analysis tools.', color='danger')

    filtered_data = data
    if decompose:
        filtered_data = handle_decompose(data, turn, tags)

    if len(filtered_data) == 0:
        return dbc.Alert('No games found matching the provided filters', color='warning')

    breakdown_data = create_deck_breakdown(filtered_data, decks)
    matchup_list = prep_matchup_spread(filtered_data)
    matchup_data = html.Div([
        html.H4('Matchups'),
        matchup_table.create_matchup_spread(matchup_list, decks, player='playing', against='against')
    ])
    return html.Div([
        breakdown_data,
        matchup_data
    ])
