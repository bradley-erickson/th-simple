from dash import html

import utils.images

def format_label(deck, hide_text=False):
    if deck is None:
        return ''
    children = [
        html.Img(
            src=utils.images.get_pokemon_icon(i),
            style={'maxHeight': '35px'}
        ) for i in deck.get('icons', [])
    ]
    name = deck.get('name')
    children.append(html.Span(name, className='d-none' if hide_text else 'ms-1'))
    return html.Div(
        children, title=name,
        className='d-flex flex-row align-items-center'
    )
