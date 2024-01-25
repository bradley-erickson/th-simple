import dash
from dash import html, callback, clientside_callback, ClientsideFunction, Output, Input
import dash_bootstrap_components as dbc

from utils import images, cards as _cards

dash.register_page(
    __name__,
    path='/tools/deck-diff',
    title='Deck Diff Analyzer',
    image='tools.png',
    description='Compare and contrast two Pokémon TCG decklists with our Deck Diff tool. Generate intuitive Venn diagrams to visualize card overlaps and differences, helping you refine your deck choices and understand key strategic variations.'
)

prefix = 'deck-diff'
decklist_a_name = f'{prefix}-decklist-a-name'
decklist_a_list = f'{prefix}-decklist-a-list'
decklist_a_title = f'{prefix}-decklist-a-title'

decklist_b_name = f'{prefix}-decklist-b-name'
decklist_b_list = f'{prefix}-decklist-b-list'
decklist_b_title = f'{prefix}-decklist-b-title'

a_only = f'{prefix}-a-only'
a_only_total = f'{a_only}-total'
overlap = f'{prefix}-overlap'
overlap_total = f'{overlap}-total'
b_only = f'{prefix}-b-only'
b_only_total = f'{b_only}-total'

layout = html.Div([
    html.H2('Deck Diff'),
    dbc.Alert(html.Ul([
        html.Li([html.Strong('Simple to Use:'), ' Input your decklists and see a Venn diagram-like comparison.']),
        html.Li([
            html.Strong('Need Assistance:'), ' Some imports may not be supported. If you encounter an issue, please submit a ',
            html.A('Feedback Form', href='/feedback', className='alert-link'), '.'
        ])
    ], className='mb-0'), id='deckdiff-info-alert', color='info', dismissable=True, persistence=True, persistence_type='local'),
    dbc.Row([
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText('Decklist A'),
                dbc.Input(id=decklist_a_name, placeholder='Name', className='inputgroup-input-fix')
            ]),
            dbc.Textarea(id=decklist_a_list, placeholder='Paste decklist here', value='')
        ], md=6),
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText('Decklist B'),
                dbc.Input(id=decklist_b_name, type='text', placeholder='Name', className='inputgroup-input-fix')
            ]),
            dbc.Textarea(id=decklist_b_list, placeholder='Paste decklist here', value='')
        ], md=6)
    ], className='gy-1 mb-1'),
    dbc.Spinner(dbc.Row([
        dbc.Col([
            html.H4(['Decklist A', html.Span(id=decklist_a_title), dbc.Badge(id=a_only_total, className='ms-1')]),
            dbc.Row(id=a_only, className='g-0')
        ], md=3),
        dbc.Col([
            html.H4(['Decklist B', html.Span(id=decklist_b_title), dbc.Badge(id=b_only_total, className='ms-1')], className='text-md-end'),
            dbc.Row(id=b_only, className='g-0')
        ], md={'size': 3, 'order': 'last'}),
        dbc.Col([
            html.H4(['Overlap', dbc.Badge(id=overlap_total, className='ms-1')], className='text-md-center'),
            dbc.Row(id=overlap, className='g-0')
        ], md=6)
    ], className='gy-1'))
])

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='update_diff_title'),
    Output(decklist_a_title, 'children'),
    Input(decklist_a_name, 'value')
)

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='update_diff_title'),
    Output(decklist_b_title, 'children'),
    Input(decklist_b_name, 'value')
)

def parse_decklist(l):
    deck = []
    if not l:
        return deck
    for c in l.split('\n'):
        if len(c.strip()) == 0:
            continue
        if not c[0].isdigit():
            continue
        c_split = c.split(' ')
        c_set = c_split[-2]
        c_num = c_split[-1]
        energy_check = c_set != 'Energy' and c_num not in _cards.ENERGY.values()
        c_set = c_set if energy_check else 'BRS'
        c_num = c_num if energy_check else c_split[2].replace('{', '').replace('}', '') if c_split[1] == 'Basic' else _cards.ENERGY[c_split[1]]
        card = {
            'card_code': f'{c_set}-{c_num.zfill(3) if energy_check else c_num}',
            'set': c_set,
            'number': c_num,
            'name': ' '.join(c_split[1:-2]),
            'count': int(c_split[0]),
        }
        card['card'] = _cards.get_card(card)
        deck.append(card)
    return deck


def clean_list(raw, mid=False):
    cards = [c['card'] for c in raw]
    cards_sorted = _cards.sort_deck(cards)
    cards_comp = [dbc.Col([
        html.Img(src=images.get_card_image(c['card_code'], 'SM'), className='w-100'),
        dbc.Badge(
            int(c['count']),
            class_name='position-absolute bottom-0 end-0 m-2 rounded-circle font-monospace border border-light',
        )
    ], className='position-relative', xs=4, md=2 if mid else 4) for c in cards_sorted]
    total = sum(c.get('count', 0) for c in cards)
    return cards_comp, total


@callback(
    Output(a_only, 'children'),
    Output(a_only_total, 'children'),
    Output(overlap, 'children'),
    Output(overlap_total, 'children'),
    Output(b_only, 'children'),
    Output(b_only_total, 'children'),
    Input(decklist_a_list, 'value'),
    Input(decklist_b_list, 'value')
)
def update_diff(a, b):
    dl_a = parse_decklist(a)
    dl_b = parse_decklist(b)
    a_dict = {(c['card_code'] if c['card']['supertype'] == 'Pokémon' else c['name']): c for c in dl_a}
    b_dict = {(c['card_code'] if c['card']['supertype'] == 'Pokémon' else c['name']): c for c in dl_b}

    in_a = []
    in_b = []
    in_both = []

    # TODO first fetch card supertypes
    # then we can ignore card_id for trainers
    overall = set(list(a_dict.keys()) + list(b_dict.keys()))
    for card in overall:
        if card in a_dict and card in b_dict:
            a_count = a_dict[card]['count']
            b_count = b_dict[card]['count']
            card_obj = a_dict[card]
            if a_count == b_count:
                in_both.append(a_dict[card])
            elif a_count > b_count:
                a_card = card_obj.copy()
                a_card['count'] = a_count - b_count
                in_a.append(a_card)
                in_both.append(b_dict[card])
            elif b_count > a_count:
                b_card = card_obj.copy()
                b_card['count'] = b_count - a_count
                in_b.append(b_card)
                in_both.append(a_dict[card])
        elif card in a_dict:
            in_a.append(a_dict[card])
        elif card in b_dict:
            in_b.append(b_dict[card])

    in_a, total_a = clean_list(in_a)
    in_b, total_b = clean_list(in_b)
    in_both, total_both = clean_list(in_both, True)

    return in_a, total_a, in_both, total_both, in_b, total_b
