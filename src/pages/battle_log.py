import base64
from collections import Counter
import dash
from dash import html, dcc, exceptions, clientside_callback, ClientsideFunction, callback, Output, Input, State, Patch, ALL, ctx, no_update
import dash_bootstrap_components as dbc
import datetime
import io
import json
import numpy as np
import pandas as pd

from components import (deck_label, matchup_table, ternary_switch,
                        archetype_builder, tags as tag_settings,
                        download_button as _download, feedback_link)
import components.navbar
import utils.data

page_title = 'Battle Journal'
page_icon = 'fa-book'

dash.register_page(
    __name__,
    path='/tools/battle-journal',
    title=page_title,
    redirect_from=['/tools/battle-log'],
    image='tools.png',
    icon=page_icon,
    description='Track your Pokémon TCG matches with our tool: Record opponents, game outcomes, notes, and more. Download your data for in-depth analysis.'
)

RESULT_COLORS = {'Win': 'success', 'Loss': 'danger', 'Tie': 'warning'}
TAG_OPTIONS = [
    'Ahead early', 'Behind early', 'Slow start', 'Lucky', 'Got donked',
    'Donked opp', 'Quick game', 'Dead drew', 'Poor prizes',
    'Punished opponent', 'Never punished', 'gg'
]

prefix = 'battle-journal'
game_store = f'{prefix}-games-store'
history = f'{prefix}-history'
analysis = f'{prefix}-analysis'
archetype_store = f'{prefix}-archetype-store'

# buttons
download_btn = f'{prefix}-download-button'
download_comp = f'{prefix}-download-component'
upload_id = f'{prefix}-upload'
clear_id = f'{prefix}-clear'
upload_alert = f'{prefix}-upload-alert'

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
analysis_filter_text = f'{analysis}-filter-text'
analysis_decompose_switch = f'{analysis}-filter-decompose-switch'
analysis_decompose_collapse = f'{analysis}-filter-decompose-collapse'
analysis_filter_toggle = f'{analysis}-filter-toggle'
turn_option = f'{analysis}-filter-turn-switch'

# settings
settings_pref = f'{prefix}-settings-tab'
settings_archetype_builder = f'{settings_pref}-archetype-builder'
settings_tags_built_in = f'{settings_pref}-tags-built-in'
settings_tags_custom = f'{settings_pref}-tags-custom'
settings_note_template = f'{settings_pref}-notes-template'
settings_reset = f'{settings_pref}-reset'


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
                dbc.Textarea(id={'type': notes, 'index': g}, maxlength=1_000),
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

# TODO set settings persistance
settings_tab = html.Div([
    html.H4('Game Settings'),
    archetype_builder.builder_plus_built(settings_archetype_builder, title='Add Custom Archetypes', persistance='local'),
    html.Div([
        html.H5('Tag Options'),
        dbc.Checklist(id=settings_tags_built_in, options=TAG_OPTIONS, value=TAG_OPTIONS, inline=True, persistence_type='local', persistence=True),
        tag_settings.create_tag_input(settings_tags_custom, existing_tags=TAG_OPTIONS, persistance='local')
    ], className='mt-2'),
    html.Div([
        html.H5('Notes Template'),
        dbc.Textarea(id=settings_note_template, persistence_type='local', persistence=True),
        dbc.Accordion(dbc.AccordionItem(html.Ol([
            html.Li('What could I have done better?'),
            html.Li('What misplays did I make?'),
        ]), title='Examples'), start_collapsed=True)
    ], className='notes-template mt-2'),
    html.Div(dcc.ConfirmDialogProvider(
        dbc.Button([html.I(className='far fa-trash-can me-1'), 'Reset Settings'], color='danger'),
        id=settings_reset,
        message='Are you sure you want to reset settings to default? This cannot be undone. Removing custom archetypes allows them to be overwritten under the same name.'
    ), className='d-inline-block float-end mt-1'),
    html.Div(className='mb-5')
])
archetype_builder.register_callbacks(settings_archetype_builder)
tag_settings.register_callbacks(settings_tags_custom)

tip_tab = html.Div([
    html.Ol([
        html.Li('Try out some opening turns without an opponent to get a feel for your deck.'),
        html.Li('Formulate and write down a plan for going first and going second.'),
        html.Li('Think about your strategy against the core meta decks.'),
        html.Li('Practice checking your prizes during your first deck search.'),
    ]),
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
                dbc.Collapse([], id=analysis_decompose_collapse),
                html.Small(id=analysis_filter_text)
            ]), id=analysis_filter_collapse)
        ]),
        _download.DownloadImageAIO(analysis, className='float-end'),
        dbc.Spinner(html.Div(id=analysis))
    ])
    fake_data = [
        {'playing': 'other', 'against': 'other', 'time': str(datetime.datetime.now()), 'result': 'Win', 'game1': {'result': 'Win', 'turn': 1, 'tags': ['Lucky', 'Slow start'], 'notes': 'Got off to a rocky start from judge, but we top decked the out.'}},
    ]
    cont = html.Div([
        html.H2([html.I(className=f'fas {page_icon} me-1'), page_title]),
        dbc.Alert(html.Ul([
            html.Li([html.Strong('Track Your Games:'), ' Log your games, view your history, and dive into detailed analysis.']),
            html.Li([html.Strong('Filter & Analyze:'), ' Easily filter your game history for better insights.']),
            html.Li([html.Strong('Data Privacy:'), " Your game data is stored locally in your browser. It's never collected. If you clear cookies or click the clear button, your data will be deleted forever."]),
            feedback_link.list_item,
        ], className='mb-0'), id='battlelog-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        dbc.Alert(dismissable=True, id=upload_alert, is_open=False),
        html.Div([
            html.Span(dcc.Upload(
                dbc.Button([html.I(className='fas fa-file-import me-1'), 'Import']),
                id=upload_id, multiple=True, accept='.json'
            ), className='d-inline-block me-1'),
            dbc.Button([html.I(className='fas fa-file-export me-1'), 'Export'], id=download_btn, class_name='me-1'),
            dcc.Download(id=download_comp),
            html.Div(dcc.ConfirmDialogProvider(
                dbc.Button([html.I(className='far fa-trash-can me-1'), 'Clear history']),
                id=clear_id,
                message='Are you sure you want to remove your gaming history? This cannot be undone.'
            ), className='d-inline-block'),
        ], className='mb-1'),
        dbc.Tabs([
            dbc.Tab(dbc.Spinner(create_options()), label='Add'),
            dbc.Tab(dbc.Row(id=history, class_name='flex-column-reverse'), label='History'),
            dbc.Tab(analysis_tab, label='Analysis'),
            # dbc.Tab(tip_tab, label='Tips'),
            dbc.Tab(settings_tab, label='Settings')
        ], className='mb-1'),
        dcc.Store(id=game_store, data=fake_data, storage_type='local'),
        dcc.Store(id=archetype_store, data={})
    ])
    return cont

# general callbacks
clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='clear_history'),
    Output(game_store, 'data', allow_duplicate=True),
    Input(clear_id, 'submit_n_clicks'),
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
    parsed_content = []
    try:
        if filename.endswith('.json'):
            parsed_content = json.loads(decoded.decode('utf-8'))
        # if 'csv' in filename:
        #     # Assume that the user uploaded a CSV file
        #     df = pd.read_csv(
        #         io.StringIO(decoded.decode('utf-8')))
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        pass
    return parsed_content


@callback(
    Output(game_store, 'data', allow_duplicate=True),
    Output(upload_alert, 'color'),
    Output(upload_alert, 'is_open'),
    Output(upload_alert, 'children'),
    Input(upload_id, 'contents'),
    State(upload_id, 'filename'),
    prevent_initial_call=True
)
def upload_files(list_of_contents, list_of_filenames):
    if list_of_contents is None:
        raise exceptions.PreventUpdate
    extended_data = []
    uploaded_info = {}
    for c, f in zip(list_of_contents, list_of_filenames):
        parsed_data = parse_file_content(c, f)
        uploaded_info[f] = len(parsed_data)
        # TODO check for empty lists to inform user there was an error
        extended_data.extend(parsed_data)
    patch = Patch()
    patch.extend(extended_data)
    content = html.Div([
        'Game uploaded:',
        html.Ul([html.Li(f'{k} - {v} matches') for k, v in uploaded_info.items()], className='mb-0')
    ])
    empty_uploads = sum(1 for k in uploaded_info if uploaded_info[k] == 0)
    color = 'success' if empty_uploads == 0 else 'danger' if len(uploaded_info) == empty_uploads else 'warning'
    return patch, color, True, content


@callback(
    Output(archetype_store, 'data'),
    Input(game_store, 'modified_timestamp'),
    Input(archetype_builder.ArchetypeBuilderAIO.ids.store(settings_archetype_builder), 'data'),
    State(game_store, 'data'),
    State(archetype_store, 'data'),
    State(components.navbar.game_preference, 'value')
)
def update_archetype_store(ts, extra_archetypes, data, current, game_preference):
    if ts is None or (len(current) > 0 and ctx.triggered_id == game_store):
        raise exceptions.PreventUpdate
    today = datetime.date.today()
    weeks_ago_3 = str(today - datetime.timedelta(21))
    min_game = min(d['time'] for d in data).split(' ')[0] if len(data) > 0 else str(today)
    start_date = min(min_game, weeks_ago_3)
    api_archetypes = utils.data.get_decks({'start_date': start_date, 'game': game_preference})
    archetypes = extra_archetypes + api_archetypes
    decks = {d['id']: d for d in archetypes}
    return current | decks


@callback(
    Output(download_comp, 'data'),
    Input(download_btn, 'n_clicks'),
    State(game_store, 'data')
)
def download_data(clicks, data):
    if clicks is None:
        raise exceptions.PreventUpdate
    return dcc.send_string(json.dumps(data, indent=2), filename=f'trainerhill-battle-log-{str(datetime.date.today())}.json')

    # TODO this old code for downloading a csv, we ought to allow this in the future.
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
    deck_options = [{'label': deck_label.format_label(d), 'value': d['id'], 'search': d['name']} for d in decks.values()]
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
    Output({'type': notes, 'index': ALL}, 'value', allow_duplicate=True),
    Input(submit, 'n_clicks'),
    State(settings_note_template, 'value'),
    prevent_initial_call=True
)

# history callbacks
def create_game(g, title):
    gtags = g['tags']
    gturn = int(g['turn']) if g['turn'] else 0
    gnote = g['notes']
    turn_text = f'went {gturn}{"st" if gturn == 1 else "nd"}' if gturn > 0 else ''
    return html.Div([
        f'{title} - {turn_text}',
        html.Span([dbc.Badge(t, color='primary', pill=True, class_name='ms-1') for t in gtags] if gtags is not None else []),
        html.P(gnote if gnote is not None else '')
    ])


def create_match(g, decks):
    g_playing = g['playing']
    g_against = g['against']
    matchup = dbc.Row([
        html.Div(
            deck_label.format_label(decks.get(
                g_playing, deck_label.create_default_deck(g_playing)
            ), hide_text_small=True), className='d-flex w-auto'),
        html.Div('vs.', className='d-flex w-auto'),
        html.Div(
            deck_label.format_label(decks.get(
                g_against, deck_label.create_default_deck(g_against)
            ), hide_text_small=True), className='d-flex w-auto'),
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
        if not m['result']:
            continue
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
                    html.Td(deck_label.format_label(decks.get(b, deck_label.create_default_deck(b)))),
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
            matchup = matchup_dict[m][a].copy()
            matchup['playing'] = m
            matchup['against'] = a
            matchup['total'] = total
            matchup['win_rate'] = round((matchup_dict[m][a]['Win'] + matchup_dict[m][a]['Tie']/3) / total * 100, 1)
            matchup_list.append(matchup)
    return matchup_list


def handle_decompose(data, turn, tags, options):
    included = set([t for t, t_val in zip(options, tags) if t_val == 1])
    excluded = set([t for t, t_val in zip(options, tags) if t_val == -1])
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
            if not included.issubset(tag_set):
                continue
            decomposed_data.append(new_g)
    return decomposed_data


@callback(
    Output(analysis, 'children'),
    Output(analysis_filter_text, 'children'),
    Input(game_store, 'modified_timestamp'),
    State(game_store, 'data'),
    Input(archetype_store, 'modified_timestamp'),
    State(archetype_store, 'data'),
    Input(analysis_decompose_switch, 'value'),
    Input({'type': analysis_filter_toggle, 'index': ALL}, 'value'),
    Input({'type': tags, 'index': 0}, 'options')
)
def update_matchups(history_ts, data, archetype_ts, decks, decompose, tags, options):
    if history_ts is None or archetype_ts is None or len(decks) == 0:
        raise exceptions.PreventUpdate
    
    turn = tags.pop(0) if len(tags) > 0 else 0

    inc_turn = turn > 0
    with_tags = any(t for t in tags if t == 1)
    without_tags = any(t for t in tags if t == -1)
    filter_text = 'Showing games '
    if inc_turn:
        filter_text += f'where you went {turn}{"st" if turn == 1 else "nd"}'
        filter_text += ', ' if with_tags and without_tags else ' '
        filter_text += 'and ' if with_tags ^ without_tags else ''
    if with_tags:
        filter_text += f'with tags [{", ".join([t for t, t_val in zip(options, tags) if t_val == 1])}]'
        filter_text += ', ' if inc_turn and without_tags else ''
        filter_text += ' and ' if without_tags else ''
    if without_tags:
        filter_text += f'without tags [{", ".join([t for t, t_val in zip(options, tags) if t_val == -1])}]'
    filter_text += '.'
    if not inc_turn and not with_tags and not without_tags:
        filter_text = 'Showing all.'

    if len(data) == 0:
        return dbc.Alert('Please add matches before accessing analysis tools.', color='danger'), filter_text

    filtered_data = data
    if decompose:
        filtered_data = handle_decompose(data, turn, tags, options)
    else:
        filter_text = 'Showing all.'

    if len(filtered_data) == 0:
        return dbc.Alert('No games found matching the provided filters', color='warning'), filter_text

    breakdown_data = create_deck_breakdown(filtered_data, decks)
    matchup_list = prep_matchup_spread(filtered_data)
    matchup_data = html.Div([
        html.H4('Matchups'),
        matchup_table.create_matchup_spread(matchup_list, decks, player='playing', against='against')
    ])
    return html.Div([
        breakdown_data,
        matchup_data
    ]), filter_text


# settings callbacks
clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='clear_settings'),
    Output(archetype_builder.ArchetypeBuilderAIO.ids.store(settings_archetype_builder), 'data', allow_duplicate=True),
    Output(settings_tags_built_in, 'values', allow_duplicate=True),
    Output(f'{settings_tags_custom}-store', 'data', allow_duplicate=True),
    Output(settings_note_template, 'value', allow_duplicate=True),
    Input(settings_reset, 'submit_n_clicks'),
    State(settings_tags_built_in, 'options'),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='update_notes_template'),
    Output({'type': notes, 'index': ALL}, 'value'),
    Input(settings_note_template, 'value'),
)

clientside_callback(
    ClientsideFunction(namespace='battle_log', function_name='add_tag_to_options'),
    Output({'type': tags, 'index': ALL}, 'options'),
    Input(settings_tags_built_in, 'value'),
    Input(f'{settings_tags_custom}-store', 'data')
)

@callback(
    Output(analysis_decompose_collapse, 'children'),
    Input(settings_tags_built_in, 'options'),
    Input(f'{settings_tags_custom}-store', 'data')
)
def update_analysis_filters(built_in, custom):
    overall = built_in + custom
    tag_filters = [ternary_switch.create_ternary_switch({'type': analysis_filter_toggle, 'index': t}, t) for t in overall]
    tag_filters.insert(0, ternary_switch.create_ternary_switch({'type': analysis_filter_toggle, 'index': turn_option}, 'Turn', options=ternary_switch.TURN_OPTIONS))
    analysis_filter_component = dbc.Row([
        dbc.Col(_filter, md=6, lg=4, xxl=3) for _filter in tag_filters
    ])
    return analysis_filter_component
