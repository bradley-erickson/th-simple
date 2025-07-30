import dash
from dash import html, dcc, callback, clientside_callback, ClientsideFunction, Output, Input, State
import dash_bootstrap_components as dbc
import datetime
import random

from components import download_button, deck_label, feedback_link, archetype_builder, help_icon
import utils.cache
import utils.colors
import utils.data
import utils.images
from utils._icon_color_mapping import ICON_COLOR_MAPPING

page_title = 'Badge Maker'
page_icon = 'fa-id-badge'

dash.register_page(
    __name__,
    path='/tools/badges',
    redirect_from=['/prototypes/badges'],
    title=page_title,
    image='tools.png',
    icon=page_icon,
    description='Create deck badges for trainers.'
)

prefix = 'badge-maker'

player_input = f'{prefix}-player-input'
deck_store = f'{prefix}-deck-store'
deck_select = f'{prefix}-deck-select'
additional_archetypes = f'{prefix}-additional-archetypes'
custom_archetypes = f'{prefix}-custom-archetypes'
custom_arch_collapse = f'{prefix}-custom-archetypes-collapse'
store_input = f'{prefix}-store-input'
color_input = f'{prefix}-color-input'
date_input = f'{prefix}-date-input'
background_input = f'{prefix}-background-input'
pronouns = f'{prefix}-pronouns'
tier = f'{prefix}-tier'
output = f'{prefix}-output'
output_trainer = f'{output}-trainer'
output_pronouns = f'{output}-pronouns'
output_tier = f'{output}-tier'
output_deck = f'{output}-deck'
output_store = f'{output}-store'
output_date = f'{output}-date'

fake_trainers = ['Ash Ketchum', 'Professor Oak', 'Iono', 'Sabrina',
                 'Blaine', 'Champion Cynthia', 'Champion Leon',
                 'Youngster Joey', 'Mallow', 'Wally']

_help_icon = f'{prefix}-help'
_help_children = html.Ul([
    html.Li([html.Strong('Create:'), ' Customize your badge']),
    html.Li([html.Strong('Share:'), ' Download an image to share']),
    feedback_link.list_item('badge')
], className='mb-0')

def layout():
    today = datetime.date.today()
    archetypes = utils.data.get_decks({'start_date': str(today - datetime.timedelta(21))})
    decks = {d['id']: d for d in archetypes}
    options = [
        dbc.Label('Trainer'),
        dbc.Input(id=player_input, value=random.choice(fake_trainers), placeholder='Trainer name...'),
        dbc.Label('Pronouns'),
        dcc.Dropdown(options=['their', 'her', 'his'], value='their', id=pronouns, clearable=False),
        dbc.Label('Deck Select'),
        dbc.InputGroup([
            html.Div(dcc.Dropdown(
                id=deck_select, placeholder='Deck played...',
                value=random.choice(list(decks.keys()))
            ), className='dcc-dropdown-inputgroup'),
            dbc.Button(html.I(className='fas fa-cog'), id=additional_archetypes),
        ]),
        dcc.Store(id=deck_store, data=decks),
        dbc.Collapse(
            dbc.CardBody([
                archetype_builder.builder_plus_built(custom_archetypes, other=[d for d in decks.keys()], persistance='session')
            ]),
            id=custom_arch_collapse
        ),
        dbc.Label('Background Color'),
        dbc.Input(id=color_input, value=None, type='color'),
        dbc.Label('Location'),
        dbc.Input(id=store_input, value='Locals', placeholder=''),
        dbc.Label('Background'),
        dcc.Dropdown(id=background_input,
                     options=['Grass', 'Fire', 'Water', 'Lightning',
                              'Psychic', 'Fighting', 'Dark', 'Metal',
                              'Dragon', 'Fairy', 'Colorless']),
        dbc.Label('Tier'),
        dcc.Dropdown(options=['League Challenge', 'League Cup', 'Regionals', 'Internationals', 'Locals', 'Online'], value='Locals', id=tier, clearable=False),
        dbc.Label('Date'),
        html.Div(dcc.DatePickerSingle(date=datetime.date.today(), id=date_input))
    ]
    cont = html.Div([
        html.Div([
            html.H2([html.I(className=f'fas {page_icon} me-1'), page_title], className='d-inline-block'),
            help_icon.create_help_icon(_help_icon, _help_children, className='align-top'),
            download_button.DownloadImageAIO(dom_id=output, className='float-end')
        ]),
        dbc.Alert(_help_children, id='badges-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
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
                    html.Div([dbc.Badge(id=output_tier, class_name='me-1'), 'badge at ', html.Strong(id=output_store)]),
                    html.Div([' on ', html.Span(id=output_date)]),
                ],id=output, class_name='text-center gym-badge', body=True),
                md=7, lg=6, xl=5, xxl=4
            )
        ], justify='around')
    ])
    return cont


for input_id, output_id in zip(
    [player_input, pronouns, store_input, tier],
    [output_trainer, output_pronouns, output_store, output_tier]
):
    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='return_self'),
        Output(output_id, 'children'),
        Input(input_id, 'value')
    )

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(custom_arch_collapse, 'is_open'),
    Input(additional_archetypes, 'n_clicks'),
    State(custom_arch_collapse, 'is_open')
)

archetype_builder.register_callbacks(custom_archetypes)

@callback(
    Output(deck_store, 'data'),
    Input(archetype_builder.ArchetypeBuilderAIO.ids.store(custom_archetypes), 'data'),
    State(deck_store, 'data'),
    Input(deck_store, 'className'),
)
def update_deck_store_with_extra(extra, current, _):
    for e in extra:
        current[e['id']] = e
    return current

@callback(
    Output(deck_select, 'options'),
    Input(deck_store, 'data'),
)
def update_deck_options(decks):
    deck_options = [{'label': deck_label.format_label(d), 'value': d['id'], 'search': d['name']} for d in decks.values()]
    return deck_options


@callback(
    Output(color_input, 'value'),
    Input(deck_select, 'value'),
    State(deck_store, 'data'),
)
def update_color_on_new_deck(deck, decks):
    if deck is None:
        raise dash.exceptions.PreventUpdate
    icon = decks[deck]['icons'][0]
    color = ICON_COLOR_MAPPING[icon]
    return utils.colors.rgb_to_hex(color)

@callback(
    Output(output_date, 'children'),
    Input(date_input, 'date')
)
def update_date_info(date):
    date_str = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
    return date_str


@callback(
    Output(output_deck, 'children'),
    Output(output, 'style'),
    Output(output, 'class_name'),
    Input(deck_select, 'value'),
    State(deck_store, 'data'),
    Input(background_input, 'value'),
    Input(color_input, 'value')
)
def update_deck_options(deck, decks, t, color):
    if deck is None:
        deck_option = ''
    else:
        deck_option = deck_label.format_label(decks[deck])
    style = {
        'backgroundColor': color,
        'color': utils.colors.text_color_for_background(color)
    }
    classes = f'text-center gym-badge {t.lower() if t is not None else ""}'
    return deck_option, style, classes
