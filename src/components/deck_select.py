import dash
from dash import html, dcc, callback, Output, Input, State, MATCH, ALL, Patch, ctx, clientside_callback
import dash_bootstrap_components as dbc
import th_helpers.scraper.limitless
import uuid

import components.deck_label
import utils.decklists
import utils.cache

LIMITLESSTCG = 'Limitless TCG'
MANUAL_ENTRY = 'Manual'


def create_deck_option(deck, icons, name):
    opt = html.Div([
        html.Span(components.deck_label.format_label({'name': deck, 'icons': icons})),
        html.Span(f'- {name}', className='ms-1')
    ], className='d-flex align-items-center')
    return opt


@utils.cache.cache.memoize(43200)
def _fetch_limitless_events():
    return th_helpers.scraper.limitless.fetch_events()


@utils.cache.cache.memoize(86400)
def _fetch_limitless_tour_decklists(tour):
    return th_helpers.scraper.limitless.fetch_decklists(tour)


@utils.cache.cache.memoize(604800)
def _fetch_limitless_decklist(url):
    limitless_decklist = th_helpers.scraper.limitless.fetch_decklist(url)
    decklist, _ = utils.decklists.parse_decklist(limitless_decklist)
    return decklist


class DeckSelectAIO(html.Div):

    class ids:
        wrapper = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'wrapper',
            'aio_id': aio_id
        }
        input_toggle = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'input_toggle',
            'aio_id': aio_id
        }
        decklist = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'decklist_store',
            'aio_id': aio_id
        }
        label = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'label',
            'aio_id': aio_id
        }
        limitless_wrapper = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'limitless_wrapper',
            'aio_id': aio_id
        }
        limitless_events = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'limitless_events',
            'aio_id': aio_id
        }
        limitless_players = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'limitless_players',
            'aio_id': aio_id
        }
        manual_wrapper = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'manual_wrapper',
            'aio_id': aio_id
        }
        manual_label = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'manual_label',
            'aio_id': aio_id
        }
        manual_input = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'manual_input',
            'aio_id': aio_id
        }
        manual_error = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'manual_error',
            'aio_id': aio_id
        }
        manual_parse = lambda aio_id: {
            'component': 'DeckSelectAIO',
            'subcomponent': 'manual_parse',
            'aio_id': aio_id
        }

    ids = ids

    def __init__(
        self,
        event=None,
        aio_id=None,
        className=None
    ):
        events = _fetch_limitless_events()
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        component = dbc.Row([
            dbc.Col([
                dbc.RadioItems(
                    options=[LIMITLESSTCG, MANUAL_ENTRY],
                    value=LIMITLESSTCG,
                    id=self.ids.input_toggle(aio_id),
                    class_name='d-inline-block'
                )
            ], xl=2, lg=3, class_name='d-flex justify-content-between align-items-start'),
            dbc.Col([
                dbc.Input(value='', placeholder='Label', id=self.ids.manual_label(aio_id)),
                dbc.Textarea(
                    value='', placeholder='Paste decklist here', id=self.ids.manual_input(aio_id),
                    size='sm', spellcheck='false', class_name='my-1'
                ),
                html.Small(id=self.ids.manual_error(aio_id)),
                dbc.Button(
                    'Parse', disabled=True, id=self.ids.manual_parse(aio_id),
                    class_name='float-end mb-1', size='sm')
            ], xl=10, lg=9, id=self.ids.manual_wrapper(aio_id)),
            dbc.Col([
                dcc.Dropdown(id=self.ids.limitless_events(aio_id), options=[{
                    'label': e[0], 'value': e[1]
                } for e in events], value=event),
                dcc.Dropdown(id=self.ids.limitless_players(aio_id))
            ], xl=10, lg=9, id=self.ids.limitless_wrapper(aio_id), class_name='deck-diff-limitless-dropdowns'),
            dcc.Store(id=self.ids.decklist(aio_id)),
            html.Div(id=self.ids.label(aio_id), className='d-none'),
            html.Hr()
        ], className='flex-grow-1')
        super().__init__(component, id=self.ids.wrapper(aio_id), className=className)

    clientside_callback(
        f'''function (val) {{
            if (val === '{LIMITLESSTCG}') {{ return ['d-none', 'deck-diff-limitless-dropdowns']; }}
            return ['', 'd-none'];
        }}
        ''',
        Output(ids.manual_wrapper(MATCH), 'class_name'),
        Output(ids.limitless_wrapper(MATCH), 'class_name'),
        Input(ids.input_toggle(MATCH), 'value')
    )

    clientside_callback(
        '''function (val) {
            if (val.length > 1) { return false; }
            return true;
        }
        ''',
        Output(ids.manual_parse(MATCH), 'disabled'),
        Input(ids.manual_input(MATCH), 'value')
    )

    @callback(
        Output(ids.limitless_players(MATCH), 'options'),
        Input(ids.limitless_events(MATCH), 'value')
    )
    def update_deck_options(tour):
        if tour is None:
            raise dash.exceptions.PreventUpdate
        decks = _fetch_limitless_tour_decklists(tour)
        options = [{
            'label': create_deck_option(d[1], d[2], d[4]),
            'value': f'{d[0]}:{d[3]}',
            'search': f'{d[1]} {d[4]}'
        } for d in decks]
        return options

    @callback(
        Output(ids.decklist(MATCH), 'data'),
        Output(ids.manual_error(MATCH), 'childen'),
        Input(ids.limitless_players(MATCH), 'value'),
        Input(ids.manual_parse(MATCH), 'n_clicks'),
        State(ids.manual_input(MATCH), 'value')
    )
    def update_selected_deck(deck, manual_clicks, manual_input):
        if ctx.triggered_id is None:
            raise dash.exceptions.PreventUpdate
        
        subcomponent = ctx.triggered_id['subcomponent']
        if subcomponent == 'limitless_players':    
            base_url = 'https://limitlesstcg.com'
            path = deck.split(':')[-1]
            decklist = _fetch_limitless_decklist(f'{base_url}{path}')
            return decklist, []
        elif subcomponent == 'manual_parse':
            decklist, errors = utils.decklists.parse_decklist(manual_input)
            error_string = f'Error parsing: {", ".join(errors)}' if len(errors) > 0 else ''
            return decklist, error_string
        raise dash.exceptions.PreventUpdate
    
    @callback(
        Output(ids.label(MATCH), 'children'),
        Input(ids.input_toggle(MATCH), 'value'),
        Input(ids.limitless_events(MATCH), 'value'),
        State(ids.limitless_events(MATCH), 'options'),
        Input(ids.limitless_players(MATCH), 'value'),
        State(ids.limitless_players(MATCH), 'options'),
        Input(ids.manual_label(MATCH), 'value')
    )
    def update_label(toggle, event, events, player, players, manual_title):
        if toggle == LIMITLESSTCG:
            if event is None or player is None:
                raise dash.exceptions.PreventUpdate
            
            label = [
                next(e['label'] for e in events if e['value'] == event),
                next(p['label'] for p in players if p['value'] == player),
            ]
            return label
        elif toggle == MANUAL_ENTRY:
            return manual_title
        raise dash.exceptions.PreventUpdate
