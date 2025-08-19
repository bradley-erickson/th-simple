from dash import html, dcc, clientside_callback, ClientsideFunction, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
from datetime import date, timedelta
import uuid

import utils.constants as c

def default_players(p):
    return p if p else 50

def default_start_date(s):
    return s if s else (date.today() - timedelta(21)).isoformat()

def default_end_date(s):
    return s if s else date.today().isoformat()

def default_platform(p):
    return p if p else 'all'

def default_game(g):
    return g if g else 'PTCG'

def default_division(d):
    if d is None or len(d) == 0:
        return ['JR', 'SR', 'MA']
    if type(d) == str:
        return [d]
    return d

class TourFiltersAIO(html.Div):

    class ids:
        players = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'player_count',
            'aio_id': aio_id
        }
        dates = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'dates_range',
            'aio_id': aio_id
        }
        platform = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'platform_radio',
            'aio_id': aio_id
        }
        platform_tooltip = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'platform_tooltip',
            'aio_id': aio_id
        }
        division = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'division',
            'aio_id': aio_id
        }
        division_collapse = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'division_collapse',
            'aio_id': aio_id
        }
        game = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'game_radio',
            'aio_id': aio_id
        }
        apply = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'apply_btn',
            'aio_id': aio_id
        }
        initial = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'initial_data',
            'aio_id': aio_id
        }
        collapse = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'collapse',
            'aio_id': aio_id
        }
        header = lambda aio_id: {
            'component': 'TourFiltersAIO',
            'subcomponent': 'header',
            'aio_id': aio_id
        }

    ids = ids

    def __init__(
        self,
        player_count=None,
        start_date=None,
        end_date=None,
        platform=None,
        game=None,
        division=None,
        aio_id=None
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        initial_data = {
            'players': default_players(player_count),
            'start_date': default_start_date(start_date),
            'end_date': end_date,
            'platform': default_platform(platform),
            'game': default_game(game),
            'division': default_division(division)
        }

        platform_text = {'all': 'on all platforms', 'inperson': 'at majors', 'online': 'online'}
        end_date_text = f" - {initial_data['end_date']}" if initial_data['end_date'] else ''
        division_text = f"in {initial_data['division']}" if platform == 'inperson' else ''
        header_text = f' - {initial_data["game"]} {initial_data["players"]} players, from {initial_data["start_date"]}{end_date_text} {platform_text[initial_data["platform"]]} {division_text}'
        filters = dbc.Card([
            html.A(
                dbc.CardHeader([
                    html.I(className='fas fa-filter me-1'),
                    html.Strong('Tournament Filters'),
                    html.Span(header_text)
                ]),
                id=self.ids.header(aio_id)
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(html.Strong('Game')),
                            dbc.RadioItems(
                                id=self.ids.game(aio_id),
                                value=initial_data['game'],
                                options=['PTCG', 'POCKET']
                            ),
                        ], md=6, lg=4, xl=3),
                        dbc.Col([
                            dbc.Label(html.Strong('Min players')),
                            dbc.Input(
                                id=self.ids.players(aio_id),
                                type='number',
                                value=initial_data['players'],
                                min=20
                            ),
                        ], md=6, lg=4, xl=3),
                        dbc.Col([
                            dbc.Label(html.Strong('Dates')),
                            html.Div(dcc.DatePickerRange(
                                id=self.ids.dates(aio_id),
                                className='w-100',
                                start_date=initial_data['start_date'],
                                end_date=initial_data['end_date'],
                                end_date_placeholder_text='Today'
                            )),
                        ], md=6, lg=4, xl=3),
                        dbc.Col([
                            dbc.Label(html.Strong([
                                'Platform',
                                html.I(className='ms-1 fas fa-circle-info', id=self.ids.platform_tooltip(aio_id)),
                                dbc.Tooltip([
                                    '"Online" gathers data exclusively from the Play LimitlessTCG tournament platform.',
                                    html.Br(),
                                    '"Majors" compiles data from players in Major tournaments, including Regionals, Special Events, Internationals, and Worlds.',
                                ], target=self.ids.platform_tooltip(aio_id))
                            ])),
                            dbc.RadioItems(
                                options=[
                                    {'value': 'all', 'label': 'Both'},
                                    {'value': 'online', 'label': 'Online'},
                                    {'value': 'inperson', 'label': 'Majors'},
                                ],
                                value=initial_data['platform'],
                                id=self.ids.platform(aio_id)
                            ),
                            dbc.Collapse([
                                dbc.Label('Division'),
                                dbc.Checklist(
                                    options={
                                        'JR': 'Juniors',
                                        'SR': 'Seniors',
                                        'MA': 'Masters'
                                    },
                                    value=initial_data['division'],
                                    id=self.ids.division(aio_id)
                                )
                            ], id=self.ids.division_collapse(aio_id), is_open=False)
                        ], md=6, lg=4, xl=3),
                    ], className='mb-1'),
                    dbc.Button(
                        'Apply',
                        id=self.ids.apply(aio_id),
                        class_name='float-end',
                    ),
                    dcc.Store(
                        id=self.ids.initial(aio_id),
                        data=initial_data
                    )
                ]),
                id=self.ids.collapse(aio_id),
            )
        ])
        super().__init__(filters)

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='disable_tour_filter_apply'),
        Output(ids.apply(MATCH), 'disabled'),
        Input(ids.players(MATCH), 'value'),
        Input(ids.dates(MATCH), 'start_date'),
        Input(ids.dates(MATCH), 'end_date'),
        Input(ids.platform(MATCH), 'value'),
        Input(ids.game(MATCH), 'value'),
        Input(ids.division(MATCH), c.DASH.VALUE),
        State(ids.initial(MATCH), 'data')
    )

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='update_tour_filter_apply_href'),
        Output(ids.apply(MATCH), 'href'),
        Input(ids.players(MATCH), 'value'),
        Input(ids.dates(MATCH), 'start_date'),
        Input(ids.dates(MATCH), 'end_date'),
        Input(ids.platform(MATCH), 'value'),
        Input(ids.game(MATCH), 'value'),
        Input(ids.division(MATCH), c.DASH.VALUE),
        Input('_pages_location', 'hash')
    )

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
        Output(ids.collapse(MATCH), 'is_open'),
        Input(ids.header(MATCH), 'n_clicks'),
        State(ids.collapse(MATCH), 'is_open')
    )

    clientside_callback(
        ClientsideFunction(namespace=c.DASH.CLIENTSIDE, function_name='toggleWithPlatformValue'),
        Output(ids.division_collapse(MATCH), c.DASH.IS_OPEN),
        Input(ids.platform(MATCH), c.DASH.VALUE)
    )


def create_tour_filter(**kwargs):
    params = {}
    params['players'] = default_players(kwargs.get('players'))
    params['start_date'] = default_start_date(kwargs.get('start_date'))
    params['end_date'] = default_end_date(kwargs.get('end_date'))
    params['platform'] = default_platform(kwargs.get('platform'))
    params['game'] = default_game(kwargs.get('game'))
    params['division'] = default_division(kwargs.get('division'))
    return params

def create_param_string(tf):
    end_string = f'&end_date={tf["end_date"]}' if 'end_date' in tf and tf['end_date'] is not None else ''
    platform_string = f'&platform={tf["platform"]}' if 'platform' in tf and tf['platform'] in ['online', 'inperson'] else ''
    divisions = tf['division']
    divisions = [divisions] if type(divisions) == str else divisions
    divisions = [f'division={d}' for d in divisions]
    divisions_string = f"&{('&').join(divisions)}" if 'platform' in tf and tf['platform'] == 'inperson' and divisions else ''
    param_str = f'?game={tf["game"]}&players={tf["players"]}&start_date={tf["start_date"]}{end_string}{platform_string}{divisions_string}'
    return param_str
