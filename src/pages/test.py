import dash
from dash import html, callback, Output, Input, ALL, Patch, ctx, State, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
from dash_extensions import EventListener

import utils.images

dash.register_page(
    __name__,
    path='/test',
    title='test',
    description='testing'
)

layout = html.Div([
    html.H2('Deck layout testing', id='header'),
    dbc.Input(id='index', value=0),
    EventListener(
        html.Div([
            html.Div([
                html.Img(src=utils.images.get_card_image(f'MEW-{str(i+1).zfill(3)}', 'XS'))
            ], id={'type': 'card_in_stack', 'index': i}, className='card-in-stack') for i in range(46)
            ], className='deck-stack'
        ), id='el',
        events=[{'event': 'wheel', 'props': ['wheelDelta']}], 
    ),
    html.Div(id='out')
])

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='update_index'),
    Output('index', 'value'),
    Input('el', 'n_events'),
    State('el', 'event'),
    State('index', 'value'),
    State({'type': 'card_in_stack', 'index': ALL}, 'id')
)

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='advance_card'),
    Output('index', 'className'),
    Input('index', 'value')
)
