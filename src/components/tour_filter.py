from dash import html, dcc, clientside_callback, ClientsideFunction, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
from datetime import date, timedelta
import uuid

def default_players(p):
    return p if p else 50

def default_start_date(s):
    return s if s else (date.today() - timedelta(21)).isoformat()

def default_end_date(s):
    return s if s else date.today().isoformat()

def default_platform(p):
    return p if p else 'all'

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
        aio_id=None
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        initial_data = {
            'players': default_players(player_count),
            'start_date': default_start_date(start_date),
            'end_date': end_date,
            'platform': default_platform(platform)
        }

        filters = dbc.Card([
            html.A(
                dbc.CardHeader([
                    html.I(className='fas fa-filter me-1'),
                    'Tournament Filters'
                ]),
                id=self.ids.header(aio_id)
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Min players'),
                            dbc.Input(
                                id=self.ids.players(aio_id),
                                type='number',
                                value=initial_data['players'],
                                min=0
                            ),
                        ], lg=4),
                        dbc.Col([
                            dbc.Label('Dates'),
                            html.Div(dcc.DatePickerRange(
                                id=self.ids.dates(aio_id),
                                className='w-100',
                                start_date=initial_data['start_date'],
                                end_date=initial_data['end_date'],
                                end_date_placeholder_text='Today'
                            )),
                        ], lg=4),
                        dbc.Col([
                            dbc.Label([
                                'Platform',
                                html.I(className='ms-1 fas fa-circle-info', id=self.ids.platform_tooltip(aio_id)),
                                dbc.Tooltip([
                                    '"Online" gathers data exclusively from the Play LimitlessTCG tournament platform.',
                                    html.Br(),
                                    '"Majors" compiles data from players who advanced to Day 2 in Major tournaments, including Regionals, Special Events, Internationals, and Worlds.',
                                ], target=self.ids.platform_tooltip(aio_id))
                            ]),
                            dbc.RadioItems(
                                options=[
                                    {'value': 'all', 'label': 'Both'},
                                    {'value': 'online', 'label': 'Online'},
                                    {'value': 'inperson', 'label': 'Majors'},
                                ],
                                value=initial_data['platform'],
                                id=self.ids.platform(aio_id)
                            ),
                        ], lg=4),
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
        State(ids.initial(MATCH), 'data')
    )

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='update_tour_filter_apply_href'),
        Output(ids.apply(MATCH), 'href'),
        Input(ids.players(MATCH), 'value'),
        Input(ids.dates(MATCH), 'start_date'),
        Input(ids.dates(MATCH), 'end_date'),
        Input(ids.platform(MATCH), 'value'),
        Input('_pages_location', 'hash')
    )

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
        Output(ids.collapse(MATCH), 'is_open'),
        Input(ids.header(MATCH), 'n_clicks'),
        State(ids.collapse(MATCH), 'is_open')
    )


def create_tour_filter(players=None, start_date=None, end_date=None, platform=None):
    params = {}
    params['players'] = default_players(players)
    params['start_date'] = default_start_date(start_date)
    params['end_date'] = default_end_date(end_date)
    params['platform'] = default_platform(platform)
    return params

def create_param_string(tf):
    end_string = f'&end_date={tf["end_date"]}' if 'end_date' in tf and tf['end_date'] is not None else ''
    platform_string = f'&platform={tf["platform"]}' if 'platform' in tf and tf['platform'] in ['online', 'inperson'] else ''
    param_str = f'?players={tf["players"]}&start_date={tf["start_date"]}{end_string}{platform_string}'
    return param_str
