import dash
from dash import html, dcc, callback, clientside_callback, ClientsideFunction, Output, Input, State, MATCH, ALL, Patch, ctx
import dash_bootstrap_components as dbc

remove_tag = 'tags_remove_tag'

def create_tag_input(id, existing_tags=None, persistance='memory'):
    if existing_tags is None:
        existing_tags = []
    custom_input = f'{id}-input'
    add_button = f'{id}-add'
    store = f'{id}-store'
    other = f'{id}-other-store'
    output = f'{id}-output'

    cont = html.Div([
        dbc.InputGroup([
            dbc.Input(id=custom_input, placeholder='Enter custom tag', value=''),
            dbc.Button('Add', id=add_button, n_clicks=0, disabled=True)
        ]),
        html.Div(id=output, className='mt-1 d-flex'),
        dcc.Store(id=store, data=[], storage_type=persistance),
        dcc.Store(id=other, data=existing_tags),
    ])
    return cont

def create_tag(value):
    contents = dbc.Badge(html.Div([
        value,
        dbc.Button(
            html.I(className='fas fa-close fa-sm text-white'),
            color='transparent',
            id={'type': remove_tag, 'index': value},
            n_clicks=0
        )
    ], className='d-flex align-items-center'))
    return contents

def register_callbacks(id):
    custom_input = f'{id}-input'
    add_button = f'{id}-add'
    store = f'{id}-store'
    other = f'{id}-other-store'
    output = f'{id}-output'

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='tag_disable_add'),
        Output(add_button, 'disabled'),
        Input(custom_input, 'value'),
        State(store, 'data'),
        State(other, 'data')
    )

    @callback(
        Output(store, 'data'),
        Output(custom_input, 'value'),
        Input(add_button, 'n_clicks'),
        State(custom_input, 'value')
    )
    def update_store(clicks, val):
        if clicks == 0:
            raise dash.exceptions.PreventUpdate
        p = Patch()
        p.append(val)
        return p, ''

    @callback(
        Output(output, 'children'),
        Input(store, 'modified_timestamp'),
        State(store, 'data')
    )
    def update_output(ts, data):
        if ts is None:
            return []
        return [html.Div(create_tag(v), className='me-1') for v in data]
    
    @callback(
        Output(store, 'data', allow_duplicate=True),
        Input({'type': remove_tag, 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def remove_tag_from_store(clicks):
        if any(c for c in clicks if c > 0):
            p = Patch()
            p.remove(ctx.triggered_id['index'])
            return p
        raise dash.exceptions.PreventUpdate
