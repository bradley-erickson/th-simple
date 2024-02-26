import dash
from dash import html, dcc, callback, clientside_callback, ClientsideFunction, Output, Input, State, MATCH, ALL, Patch, ctx
import dash_bootstrap_components as dbc
import random
import uuid

import components.deck_label
import components.archetype_builder
import utils.pokemon

remove_tag = 'archetype_remove_tag_type'

pokemon_options = [{
    'label': components.deck_label.format_label(deck),
    'value': deck['id'],
    'search': deck['name']
} for deck in utils.pokemon.pokemon_as_decks]

class ArchetypeBuilderAIO(html.Div):

    class ids:
        icons = lambda aio_id: {
            'component': 'ArchetypeBuilderAIO',
            'subcomponent': 'icon_dropdown',
            'aio_id': aio_id
        }
        name = lambda aio_id: {
            'component': 'ArchetypeBuilderAIO',
            'subcomponent': 'name_input',
            'aio_id': aio_id
        }
        add = lambda aio_id: {
            'component': 'ArchetypeBuilderAIO',
            'subcomponent': 'add_btn',
            'aio_id': aio_id
        }
        store = lambda aio_id: {
            'component': 'ArchetypeBuilderAIO',
            'subcomponent': 'data_store',
            'aio_id': aio_id
        }
        other = lambda aio_id: {
            'component': 'ArchetypeBuilderAIO',
            'subcomponent': 'other_store',
            'aio_id': aio_id
        }
        warning = lambda aio_id: {
            'component': 'ArchetypeBuilderAIO',
            'subcomponent': 'warning',
            'aio_id': aio_id
        }


    ids = ids

    def __init__(
        self,
        other=None,
        persistance='memory',
        aio_id=None
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        if other is None:
            other = []

        random.shuffle(pokemon_options)
        component = [
            dbc.Form([
                dbc.Label('Icons'),
                dcc.Dropdown(id=self.ids.icons(aio_id), options=pokemon_options, multi=True, placeholder='Select Pokémon', value=[]),
                dbc.Label('Name'),
                dbc.Input(type='text', value='', id=self.ids.name(aio_id), placeholder='Name the deck'),
                dbc.FormText('Please select icons and input name.',id=self.ids.warning(aio_id), class_name='text-muted'),
                dbc.Button(['Add Deck'], id=self.ids.add(aio_id), n_clicks=0, disabled=True, class_name='mt-1 float-end'),
            ]),
            dcc.Store(id=self.ids.store(aio_id), data=[], storage_type=persistance),
            dcc.Store(id=self.ids.other(aio_id), data=other)
        ]
        super().__init__(component)

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='archetype_builder_disbaled_add'),
        Output(ids.add(MATCH), 'disabled'),
        Output(ids.warning(MATCH), 'children'),
        Input(ids.icons(MATCH), 'value'),
        Input(ids.name(MATCH), 'value'),
        State(ids.store(MATCH), 'data'),
        State(ids.other(MATCH), 'data')
    )

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='archetype_builder_add_deck'),
        Output(ids.store(MATCH), 'data'),
        Output(ids.icons(MATCH), 'value'),
        Output(ids.name(MATCH), 'value'),
        Input(ids.add(MATCH), 'n_clicks'),
        State(ids.icons(MATCH), 'value'),
        State(ids.name(MATCH), 'value'),
        State(ids.store(MATCH), 'data')
    )


def create_archetype_tag_list(data):
    return [html.Div(create_arcehtype_tag(deck), className='me-1') for deck in data]

def create_arcehtype_tag(arch):
    contents = dbc.Badge(html.Div([
        components.deck_label.format_label(arch),
        dbc.Button(
            html.I(className='fas fa-close fa-sm text-white'),
            color='transparent',
            id={'type': remove_tag, 'index': arch['id']},
            n_clicks=0
        )
    ], className='d-flex'))
    return contents

def builder_plus_built(id, other=None, title='Archetype Builder', persistance='memory'):
    if other is None:
        other = []
    out_div = f'{id}-out'
    layout = html.Div([
        html.H5(title),
        ArchetypeBuilderAIO(aio_id=id, other=other, persistance=persistance),
        html.Div(id=out_div, className='mt-1 d-flex')
    ])
    return layout


def register_callbacks(id):
    out_div = f'{id}-out'

    @callback(
        Output(out_div, 'children'),
        Input(ArchetypeBuilderAIO.ids.store(id), 'modified_timestamp'),
        State(ArchetypeBuilderAIO.ids.store(id), 'data')
    )
    def update_children(ts, data):
        if ts is None:
            raise dash.exceptions.PreventUpdate
        tag_list = create_archetype_tag_list(data)
        return tag_list


    @callback(
        Output(ArchetypeBuilderAIO.ids.store(id), 'data', allow_duplicate=True),
        Input({'type': remove_tag, 'index': ALL}, 'n_clicks'),
        State(ArchetypeBuilderAIO.ids.store(id), 'data'),
        prevent_initial_call=True
    )
    def remove_from_list(clicks, curr):
        if any(c for c in clicks if c > 0):
            matched = next(i for i in curr if i['id'] == ctx.triggered_id['index'])
            p = Patch()
            p.remove(matched)
            return p
        raise dash.exceptions.PreventUpdate
    return True