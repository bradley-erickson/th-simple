import base64
from collections import defaultdict
import dash
from dash import html, dcc, callback, Output, Input, State, ALL, ctx, Patch, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import datetime
import xml.etree.ElementTree as ET

from components import deck_label, matchup_table, breakdown, download_button, navbar, feedback_link
import utils.data
import utils.date

dash.register_page(
    __name__,
    path='/prototypes/tournament-meta-report',
    title='Tournament Meta Report (beta)',
    description='Upload .tdf files, input decks, and see meta overview.',
    icon='fa-chart-bar'
)

prefix = 'tour-meta-report'
store = f'{prefix}-store'
clear_id = f'{prefix}-clear'
tabs = f'{prefix}-tabs'

# upload tab
upload_prefix = f'{prefix}-upload-tab'
upload_comp = f'{upload_prefix}-comp'
upload_tab = html.Div([
    dcc.Upload(
        id=upload_comp,
        children=html.Div([
            'Drag n\' drop or ',
            html.A('click to select'),
            ' *.tdf files'
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    )
])

# roster tab
roster_prefix = f'{prefix}-roster-tab'
roster_table = f'{roster_prefix}-table'
roster_deck_select = f'{roster_prefix}-deck-select'
roster_player = f'{roster_prefix}-player-row'
roster_store = f'{roster_prefix}-store'
roster_archetype_store = f'{roster_prefix}-archetype-store'
roster_tab = html.Div([
    dbc.Table([
        html.Thead([html.Tr([
            html.Th('Player'),
            html.Th('Deck')
        ])]),
        html.Tbody(id=roster_table)
    ], striped=True),
    dcc.Store(id=roster_store, data={}, storage_type='local')
])

# report tab
report_prefix = f'{prefix}-report-tab'
report_information = f'{prefix}-information'
report_breakdown = f'{report_prefix}-breakdown'
report_matchup = f'{report_prefix}-matchup'
report_wrapper = f'{report_prefix}-wrapper'
report_tab = html.Div([
    html.Div('No data is currently available.', id=report_information),
    html.H4('Breakdown'),
    html.Div(id=report_breakdown),
    html.H4('Matchups'),
    html.Div(id=report_matchup)
], id=report_wrapper, className='p-1')

def layout():
    archetypes = utils.data.get_decks({'start_date': datetime.date.today() - datetime.timedelta(days=21)})
    decks = {d['id']: d for d in archetypes}
    return html.Div([
        html.Div([
            html.H2('Tournament Meta Report', className='d-inline-block'),
            html.Div(dcc.ConfirmDialogProvider(
                dbc.Button([html.I(className='far fa-trash-can me-1'), 'Clear Data']),
                id=clear_id,
                message='Are you sure you want to clear the tournament data? This cannot be undone.'
            ), className='d-inline-block float-end'),
            # TODO make the download button only appear when the report tab is active
            download_button.DownloadImageAIO(dom_id=report_wrapper, className='float-end me-1'),
        ]),
        dbc.Alert(html.Ul([
            html.Li([html.Strong('Prototype dashboard:'), ' This dashboard is a work in progress. Some things are not yet finalized.']),
            html.Li([html.Strong('Purpose:'), ' This dashboard allows Tournamet Organizers to see a snapshot of the local meta.']),
            html.Li([html.Strong('Usage:'), ' Upload a tdf, choose a deck for each player, inpsect breakdown and matchups.']),
            html.Li([html.Strong('Data Privacy:'), " The uploaded data is processed to display relevant information, but no information is collected. If you clear cookies or click the clear button, your data will be deleted forever."]),
            feedback_link.list_item,
        ], className='mb-0'), id='tour-meta-report-info-alert', color='info'),
        dbc.Tabs([
            dbc.Tab(upload_tab, label='Upload', tab_id=upload_prefix),
            dbc.Tab(roster_tab, label='Roster', tab_id=roster_prefix),
            dbc.Tab(report_tab, label='Report', tab_id=report_prefix),
        ], id=tabs, persistence=True, persistence_type='local'),
        dcc.Store(id=store, data={}, storage_type='local'),
        dcc.Store(id=roster_archetype_store, data=decks)
    ])

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='clear_tour_report_data'),
    Output(store, 'data', allow_duplicate=True),
    Output(roster_store, 'data', allow_duplicate=True),
    Output(tabs, 'active_tab', allow_duplicate=True),
    Input(clear_id, 'submit_n_clicks'),
    prevent_initial_call=True
)


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def parse_file_content(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    parsed_content = {}
    try:
        if filename.endswith('.tdf'):
            root = ET.fromstring(decoded)
            parsed_content = etree_to_dict(root)
            return parsed_content
        raise NameError('Unable to parse filename.')
    except Exception as e:
        raise e

@callback(
    Output(store, 'data'),
    Output(roster_store, 'data'),
    Output(tabs, 'active_tab'),
    Input(upload_comp, 'contents'),
    State(upload_comp, 'filename'),
    State(upload_comp, 'last_modified'),
    State(roster_store, 'data')
)
def upload_data(contents, filename, last_mod, curr_roster):
    if contents is None:
        raise dash.exceptions.PreventUpdate
    try:
        tdf_contents = parse_file_content(contents, filename)
    except Exception:
        raise dash.exceptions.PreventUpdate
    
    players_list = tdf_contents['tournament']['players']['player']
    for p in players_list:
        p_id = p['@userid']
        if p_id in curr_roster:
            continue
        curr_roster[p_id] = p
        curr_roster[p_id]['deck'] = 'other'
    return tdf_contents, curr_roster, roster_prefix


def create_roster_row(player, decks):
    name = player['firstname'] + ' ' + player['lastname']
    id = player['@userid']
    return html.Tr([
        html.Td(name),
        html.Td(dcc.Dropdown(
            id={'index': id, 'type': roster_deck_select},
            options=decks,
            value=player.get('deck', 'other'),
            clearable=False
        ), className='w-50')
    ], id={'index': id, 'type': roster_player}, className='tour-meta-report-row')


@callback(
    Output(roster_table, 'children'),
    Input(roster_store, 'modified_timestamp'),
    State(roster_store, 'data'),
    State(roster_archetype_store, 'data')
)
def update_roster_table(ts, data, decks):
    if ts is None:
        raise dash.exceptions.PreventUpdate
    deck_options = [{'label': deck_label.format_label(d), 'value': d['id'], 'search': d['name']} for d in decks.values()]
    rows = []
    for player in data.values():
        rows.append(create_roster_row(player, deck_options))
    return rows


@callback(
    Output(roster_store, 'data', allow_duplicate=True),
    Input({'type': roster_deck_select, 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def update_roster(values):
    if len(ctx.triggered) > 1 or ctx.triggered_id is None:
        raise dash.exceptions.PreventUpdate
    idx = ctx.triggered_id['index']
    patch = Patch()
    patch[idx]['deck'] = ctx.triggered[0]['value']
    return patch


@callback(
    Output(report_information, 'children'),
    Input(store, 'modified_timestamp'),
    State(store, 'data'),
)
def update_report_information(tdf_ts, tdf):
    if tdf_ts is None:
        raise dash.exceptions.PreventUpdate
    if 'tournament' not in tdf:
        return 'No data is currently available.'

    ti = tdf['tournament']['data']
    return [
        html.H3(ti['name']),
        html.P([
            f'{ti["city"]}, {ti["state"]}, {ti["country"]}',
            html.Br(),
            utils.date.convert_datestring(ti['startdate'])
        ])
    ]


@callback(
    Output(report_breakdown, 'children'),
    Input(roster_store, 'modified_timestamp'),
    State(roster_store, 'data'),
    Input(store, 'modified_timestamp'),
    State(store, 'data'),
    State(roster_archetype_store, 'data'),
    Input(dbt.ThemeSwitchAIO.ids.switch(navbar.theme), 'value')
)
def update_report_breakdown(roster_ts, roster, tdf_ts, tdf, archetypes, theme):
    if roster_ts is None or tdf_ts is None:
        raise dash.exceptions.PreventUpdate
    deck_counts = {}
    for player in roster.values():
        p_deck = player['deck']
        if p_deck not in deck_counts:
            deck_counts[p_deck] = 0
        deck_counts[p_deck] += 1
    decks = []
    for d in deck_counts:
        count = deck_counts[d]
        decks.append({
            'deck': d,
            'count': count,
            'label': deck_label.format_label(archetypes[d]),
            'href': None,
            'name': archetypes[d]['name']
        })
    sorted_decks = sorted(decks, key=lambda x: x['count'], reverse=True)
    bd_list = breakdown.create_ordered_list(sorted_decks, key='count')
    bd_graph = breakdown.create_pie_chart(sorted_decks, theme)
    output = dbc.Row([
        dbc.Col(bd_list, md=6, lg=7, xxl=8),
        dbc.Col(bd_graph, md=6, lg=5, xxl=4)
    ])
    return output


@callback(
    Output(report_matchup, 'children'),
    Input(roster_store, 'modified_timestamp'),
    State(roster_store, 'data'),
    Input(store, 'modified_timestamp'),
    State(store, 'data'),
    State(roster_archetype_store, 'data')
)
def update_report_matchups(roster_ts, roster, tdf_ts, tdf, decks):
    if roster_ts is None or tdf_ts is None:
        raise dash.exceptions.PreventUpdate
    if 'tournament' not in tdf:
        return ''
    matchups = {}
    rounds = tdf['tournament']['pods']['pod']['rounds']['round']
    for round_info in rounds:
        round_matches = round_info['matches']['match']
        for match in round_matches:
            if 'player1' in match and 'player2' in match:
                p1_deck = roster[match['player1']['@userid']]['deck']
                p2_deck = roster[match['player2']['@userid']]['deck']
                winner = match['@outcome']
                if p1_deck not in matchups:
                    matchups[p1_deck] = {}
                if p2_deck not in matchups:
                    matchups[p2_deck] = {}

                if p1_deck not in matchups[p2_deck]:
                    matchups[p2_deck][p1_deck] = {'wins': 0, 'losses': 0, 'ties': 0}
                if p2_deck not in matchups[p1_deck]:
                    matchups[p1_deck][p2_deck] = {'wins': 0, 'losses': 0, 'ties': 0}
                if winner == '1':
                    matchups[p2_deck][p1_deck]['losses'] += 1
                    matchups[p1_deck][p2_deck]['wins'] += 1
                elif winner == '2':
                    matchups[p2_deck][p1_deck]['wins'] += 1
                    matchups[p1_deck][p2_deck]['losses'] += 1
                elif winner == '3':
                    matchups[p2_deck][p1_deck]['ties'] += 1
                    matchups[p1_deck][p2_deck]['ties'] += 1
                else:
                    pass
    matchup_list = []
    for m in matchups:
        for a in matchups[m]:
            total = matchups[m][a]['wins'] + matchups[m][a]['losses'] + matchups[m][a]['ties']
            if total == 0:
                continue
            matchup = matchups[m][a].copy()
            matchup['playing'] = m
            matchup['against'] = a
            matchup['total'] = total
            matchup['win_rate'] = round((matchups[m][a]['wins'] + matchups[m][a]['ties']/3) / total * 100, 1)
            matchup_list.append(matchup)
    return matchup_table.create_matchup_spread(matchup_list, decks, player='playing', against='against')
