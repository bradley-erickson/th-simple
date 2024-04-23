import dash
from dash import html, dcc

dash.register_page(
    __name__,
    path='/tools',
    title='Tools',
    image='tools.png',
    description='Boost your Pokémon TCG play with our tools: Tier lists, deck comparisons, game notes. Unique insights for casual and competitive gamers.'
)

def layout():
    tool_pages = {page['title']: page for page in dash.page_registry.values() if page['path'].startswith('/tools/')}
    links = [html.Div([
        html.H3(dcc.Link(p['title'], href=p['path']), id=p['module'].replace('pages.', '')),
        html.P(p['description'])
    ]) for p in tool_pages.values()]
    return html.Div([
        html.H2('Tools'),
        html.Div(links)
    ])
