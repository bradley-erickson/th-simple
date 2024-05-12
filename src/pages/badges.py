import dash
from dash import html, dcc, callback, clientside_callback, ClientsideFunction, Output, Input, State
import dash_bootstrap_components as dbc
import datetime
# import Pylette

from components import download_button, deck_label, feedback_link
import utils.cache
import utils.colors
import utils.data
import utils.images

dash.register_page(
    __name__,
    path='/prototypes/badges',
    title='Badge Maker',
    image='tools.png',
    icon='fa-id-badge',
    description='Create deck badges for trainers.'
)

prefix = 'badge-maker'

player_input = f'{prefix}-player-input'
deck_store = f'{prefix}-deck-store'
deck_select = f'{prefix}-deck-select'
store_input = f'{prefix}-store-input'
pronouns = f'{prefix}-pronouns'
output = f'{prefix}-output'
output_trainer = f'{output}-trainer'
output_pronouns = f'{output}-pronouns'
output_deck = f'{output}-deck'
output_store = f'{output}-store'

def layout():
    today = datetime.date.today()
    archetypes = utils.data.get_decks({'start_date': str(today - datetime.timedelta(21))})
    decks = {d['id']: d for d in archetypes}
    options = [
        dbc.Label('Trainer'),
        dbc.Input(id=player_input, value='Ash Ketchum', placeholder='Trainer name...'),
        dbc.Label('Pronouns'),
        dcc.Dropdown(options=['their', 'her', 'his'], value='their', id=pronouns, clearable=False),
        dbc.Label('Deck Select'),
        dcc.Dropdown(id=deck_select, placeholder='Deck played...', value='other'),
        dcc.Store(id=deck_store, data=decks),
        dbc.Label('Location'),
        dbc.Input(id=store_input, value='Locals', placeholder='')
    ]
    cont = html.Div([
        html.Div([
            html.H2('Badge Maker', className='d-inline-block'),
            download_button.DownloadImageAIO(dom_id=output)
        ], className='d-flex justify-content-between'),
        dbc.Alert(html.Ul([
            html.Li([html.Strong('Prototype dashboard:'), ' This dashboard is a work in progress. Some things are not yet finalized.']),
            html.Li([html.Strong('Purpose:'), ' This dashboard allows users to create badges for winning a tournament with a specific deck.']),
            feedback_link.list_item,
        ], className='mb-0'), id='tour-meta-report-info-alert', color='info'),
        dbc.Row([
            dbc.Col(
                dbc.Form(options),
                md=5, lg=6, xl=5, xxl=4
            ),
            dbc.Col(
                dbc.Card([
                    html.H4(id=output_trainer),
                    html.Div(['earned ', html.Span(id=output_pronouns)], className='mb-2'),
                    html.H4(id=output_deck, className='d-flex justify-content-around'),
                    html.Div(['badge at ', html.Strong(id=output_store), ' on ', datetime.datetime.now().strftime("%B %d, %Y")]),
                ],id=output, class_name='text-center', body=True),
                md=7, lg=6, xl=5, xxl=4
            )
        ], justify='around')
    ])
    return cont


for input_id, output_id in zip(
    [player_input, pronouns, store_input],
    [output_trainer, output_pronouns, output_store]
):
    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='return_self'),
        Output(output_id, 'children'),
        Input(input_id, 'value')
    )


@callback(
    Output(deck_select, 'options'),
    Input(deck_store, 'data')
)
def update_deck_options(decks):
    deck_options = [{'label': deck_label.format_label(d), 'value': d['id'], 'search': d['name']} for d in decks.values()]
    return deck_options


# @utils.cache.cache.memoize(timeout=0)
# def extract_color(icon):
#     url = utils.images.get_pokemon_icon(icon) if icon != 'substitute' else 'https://www.trainerhill.com/assets/substitute.png'
#     local_palette = Pylette.extract_colors(image_url=url, sort_mode='frequency', mode='MC')
#     local_palette = [l.rgb for l in local_palette]
#     return local_palette


@callback(
    Output(output_deck, 'children'),
    # Output(output, 'style'),
    Input(deck_select, 'value'),
    State(deck_store, 'data')
)
def update_deck_options(deck, decks):
    if deck is None:
        raise dash.exceptions.PreventUpdate
    deck_options = deck_label.format_label(decks[deck])
    # palette = []
    # for icon in decks[deck]['icons']:
    #     palette.append(extract_color(icon))
    # style = {
    #     'backgroundColor': f'rgb{palette[0][1]}',
    #     'color': utils.colors.text_color_for_background(palette[0][1])
    # }
    return deck_options
