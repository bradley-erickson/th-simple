import dash
from dash import html, dcc, clientside_callback, ClientsideFunction, callback, Output, Input, State, ALL, MATCH
import dash_bootstrap_components as dbc
from dash_extensions import EventListener
import random

from components import feedback_link, help_icon
import components.deck_select
import utils.cards
import utils.decklists
import utils.images

description = 'Hone your Pokémon TCG skills with our tool. Practice figuring out your prizes to refine your gameplay strategy.'

page_title = 'Prize Checker'
page_icon = 'fa-magnifying-glass'

dash.register_page(
    __name__,
    path='/tools/prize-checker',
    title=page_title,
    icon=page_icon,
    image='tools.png',
    description=description
)

prefix = 'prize-checker'

_help_icon = f'{prefix}-help'
_help_children = html.Ul([
    html.Li([html.Strong('Set Card Priorities:'), ' Input your decklists and set card priorities.']),
    html.Li([html.Strong('Determine Prize Cards:'), ' Scroll through your deck to figure out which cards are prized.']),
    feedback_link.list_item
], className='mb-0')

EXAMPLE = '''Pokémon (18)
2 Charmander MEW 4
1 Charmander PR-SV 47
1 Charmander OBF 26
1 Charmeleon OBF 27
3 Charizard ex OBF 125
2 Pidgey MEW 16
2 Pidgeot ex OBF 164
1 Radiant Charizard CRZ 20
1 Rotom V CRZ 45
1 Lumineon V BRS 40
1 Mew CEL 11
1 Manaphy BRS 41
1 Jirachi PAR 126

Trainer (36)
4 Arven OBF 186
3 Boss's Orders PAL 172
3 Iono PAL 185
1 Professor's Research SVI 189
4 Rare Candy SVI 191
4 Ultra Ball SVI 196
4 Battle VIP Pass FST 225
2 Super Rod PAL 188
2 Lost Vacuum CRZ 135
1 Counter Catcher PAR 160
1 Level Ball BST 129
1 Switch SVI 194
1 Forest Seal Stone SIT 156
1 Choice Belt PAL 176
1 Technical Machine: Devolution PAR 177
2 Artazon PAL 171
1 Collapsed Stadium BRS 137

Energy (6)
6 Fire Energy 2'''

# decklist tab
d_prefix = f'{prefix}-decklist'
d_store = f'{d_prefix}-store'
d_output = f'{d_prefix}-output'
d_card = f'{d_output}-card'


def create_decklist_tab():
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.I(className='fas fa-pen-to-square me-1'),
                'Edit Decklist'
            ]),
            dbc.CardBody(dbc.Spinner(
                components.deck_select.DeckSelectAIO(aio_id=d_store, className='d-flex flex-grow-1')
            ))
        ]),
        html.H4('Set Priority'),
        dbc.Spinner([
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th('#', title='Card count'),
                    html.Th('Card', title='Card name'),
                    html.Th('Priority', title='Priority')
                ])),
                html.Tbody([], id=d_output)
            ])
        ])
    ])


# practice tab
p_prefix = f'{prefix}-practice'
p_header = f'{p_prefix}-header'
p_collapse = f'{p_prefix}-collapse'
p_reset = f'{prefix}-reset'
p_index = f'{p_prefix}-index'
p_wheel = f'{p_prefix}-wheel'
p_deck = f'{p_prefix}-deck'
p_card = f'{p_deck}-card'
p_hand = f'{p_prefix}-hand'
p_prize = f'{p_prefix}-prize'
p_prize_hidden = f'{p_prefix}-prize-hidden'
p_index = f'{p_prefix}-index'
p_out = f'{p_prefix}-output'
p_prized = f'{p_out}-prized-count'
p_status = f'{p_out}-prized-status'
practice_tab = html.Div([
    html.Div([
        html.H4('Cards in Deck', className=''),
        dbc.Button(
            [html.I(className='fas fa-shuffle'), html.Span('Shuffle', className='ms-1 d-none d-md-inline-block')],
            id=p_reset, n_clicks=0, class_name='ms-auto', title='Shuffle'
        )
    ], className='d-flex'),
    dbc.Input(id=p_index, value=0, class_name='d-none'),
    EventListener(
        html.Div([], className='deck-stack', id=p_deck),
        id=p_wheel, logging=True,
        events=[{'event': 'wheel', 'props': ['wheelDelta']}],
    ),
    html.H4('Cards known', className='d-inline-block'),
    html.I(className='ms-1 fas fa-circle-info', id='known'),
    dbc.Tooltip('Draw 7 plus 1 for turn start', target='known'),
    dbc.Row([], id=p_hand, class_name='g-1'),
    html.H4(html.A('Show Prizes', id=p_header)),
    dbc.Collapse(dbc.CardBody([
        dbc.Row([], id=p_prize_hidden, class_name='g-1')
    ]), id=p_collapse, is_open=False),
    dcc.Store(data=[], id=p_prize),
    html.H4('Guess Prizes'),
    dbc.Table([
        html.Thead(html.Tr([
            html.Th('Card', title='Card name', className='w-100'),
            html.Th('# Prized', title='Number of cards prized', className='text-nowrap'),
            html.Th(html.I(className='fas fa-question mx-1'))
        ])),
        html.Tbody([], id=p_out)
    ]),
])

# tips tab
tips_tab = html.Div([
    html.Ul([

    ])
])

# settings tab
settings_prefix = f'{prefix}-settings'
settings_start = f'{settings_prefix}-start'
settings_order = f'{settings_prefix}-order'
settings_tab = html.Div([
    html.H4('Scrolling Settings'),
    dbc.Label('Start from'),
    dbc.RadioItems({'front': 'Front', 'back': 'Back'}, value='front', id=settings_start, inline=True),
    dbc.Label('Order'),
    dbc.RadioItems({'ltr': 'Left to Right', 'rtl': 'Right to Left'}, value='ltr', id=settings_order, inline=True)
])


def layout():
    return html.Div([
        html.Div([
            html.H2([html.I(className=f'fas {page_icon} me-1'), page_title], className='d-inline-block'),
            help_icon.create_help_icon(_help_icon, _help_children, className='align-top'),
        ]),
        dbc.Alert(_help_children, id='prizechecker-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
        dbc.Tabs([
            dbc.Tab(create_decklist_tab(), label='List'),
            dbc.Tab(practice_tab, label='Practice'),
            # dbc.Tab(tips_tab, label='Tips'),
            # dbc.Tab(settings_tab, label='Settings')
        ], class_name='mb-1')
    ])


# decklist tab callbacks
clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(p_collapse, 'is_open', allow_duplicate=True),
    Input(p_header, 'n_clicks'),
    State(p_collapse, 'is_open'),
    prevent_initial_call=True
)


@callback(
    Output(d_output, 'children'),
    Input(components.deck_select.DeckSelectAIO.ids.decklist(d_store), 'data'),
)
def update_decklist_deck(data):
    out = []
    for card in data:
        id = card['card_code']
        out.append(html.Tr([
            
            dbc.Popover(
                html.Img(src=utils.images.get_card_image(id, 'SM')),
                target=id,
                trigger='hover',
                placement='bottom'
            ),
            html.Td(card['count']),
            html.Td(f"{card['name']} {id}", className='w-75'),
            html.Td(dbc.RadioItems(
                list(range(5)),
                className='btn-group btn-group-sm',
                inputClassName='btn-check',
                labelClassName='btn btn-outline-primary',
                labelCheckedClassName='active',
                value=0,
                id={'type': d_card, 'index': id}
            ), className='radio-group'),
        ], className='prize-check-row', id=id))
    return out


# practice tab callbacks
clientside_callback(
    ClientsideFunction(namespace='prize_checker', function_name='update_event_listener'),
    Output(p_deck, 'id'),
    Input(p_deck, 'id')
)

clientside_callback(
    ClientsideFunction(namespace='prize_checker', function_name='update_index'),
    Output(p_index, 'value'),
    Input(p_wheel, 'n_events'),
    State(p_wheel, 'event'),
    State(p_index, 'value'),
    State(p_deck, 'children')
)

clientside_callback(
    ClientsideFunction(namespace='prize_checker', function_name='advance_card'),
    Output(p_index, 'className'),
    Input(p_index, 'value')
)

@callback(
    Output(p_deck, 'children'),
    Output(p_hand, 'children'), 
    Output(p_prize_hidden, 'children'),
    Output(p_prize, 'data'),
    Output({'type': p_prized, 'index': ALL}, 'value'),
    Input(components.deck_select.DeckSelectAIO.ids.decklist(d_store), 'data'),
    Input(p_reset, 'n_clicks'),
    State({'type': p_prized, 'index': ALL}, 'value')
)
def update_cards_in_deck(store, clicks, outputs):
    decomposed = []
    for card in store:
        for i in range(card.get('count', 0)):
            decomposed.append(card)

    random.shuffle(decomposed)
    hand = [dbc.Col(
        html.Img(src=utils.images.get_card_image(c.get('card_code', None), 'XS'), className='w-100'),
        xs=3, sm=2, md=2, lg=1
        ) for c in decomposed[:8]
    ]
    prizes = decomposed[8:14]
    deck = [
            html.Div([
                html.Img(src=utils.images.get_card_image(c.get('card_code', None), 'XS'))
            ], className='card-in-stack') for c in decomposed[14:]
    ]
    prize_cards = [dbc.Col(
        html.Img(src=utils.images.get_card_image(c.get('card_code', None), 'XS'), className='w-100'),
        xs=3, sm=2, md=2, lg=1
        ) for c in prizes
    ]
    return deck, hand, prize_cards, prizes, [None for i in range(len(outputs))]


@callback(
    Output(p_out, 'children'),
    Input({'type': d_card, 'index': ALL}, 'value'),
    Input(components.deck_select.DeckSelectAIO.ids.decklist(d_store), 'data'),
)
def ask_about_prizes(prios, data):
    top_cards = []
    for p, d in zip(prios, data):
        if p is None:
            continue
        d['priority'] = p
        top_cards.append(d)
    top_cards = sorted(top_cards, key=lambda x: x['priority'], reverse=True)
    output = []
    curr_prior = 100
    for card in top_cards:
        id = card['card_code']
        if card['priority'] != curr_prior:
            curr_prior = card['priority']
            output.append(html.Tr([
                html.Td(f'Priority: {curr_prior}'), html.Td(), html.Td()
            ]))
        output.append(html.Tr([
            html.Td(f"{card['name']} {id}"),
            html.Td(dbc.RadioItems(
                list(range(min(7, card['count']+1))),
                className='btn-group btn-group-sm',
                inputClassName='btn-check',
                labelClassName='btn btn-outline-primary',
                labelCheckedClassName='active',
                value=None,
                id={'type': p_prized, 'index': id}
            ), className='radio-group'),
            html.Td(html.I(
                id={'type': p_status, 'index': id}
            ))
        ], className='prize-check-row', id=id))
    return output

clientside_callback(
    ClientsideFunction(namespace='prize_checker', function_name='check_status'),
    Output({'type': p_status, 'index': MATCH}, 'className'),
    Input({'type': p_prized, 'index': MATCH}, 'value'),
    State(p_prize, 'data')
)
