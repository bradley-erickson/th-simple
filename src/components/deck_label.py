from dash import html

import utils.images

def format_label(deck, hide_text=False, hide_text_small=False):
    if deck is None:
        return ''
    children = [
        html.Img(
            src=utils.images.get_pokemon_icon(i),
            style={'maxHeight': '35px'}
        ) for i in deck.get('icons', [])
    ]
    name = deck.get('name')
    children.append(html.Span(name, className='d-none' if hide_text else 'd-none d-md-inline-block' if hide_text_small else 'ms-1'))
    return html.Div(
        children, title=name,
        className='d-flex flex-row align-items-center'
    )

def create_default_deck(id):
    id_fix = 'other' if id is None else id
    return {'id': id_fix, 'name': id_fix.title(), 'icons': ['substitute']}
