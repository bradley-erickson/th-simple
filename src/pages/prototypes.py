import dash
from dash import html, dcc

dash.register_page(
    __name__,
    path='/prototypes',
    title='Prototypes',
)

def layout():
    tool_pages = {page['title']: page for page in dash.page_registry.values() if page['path'].startswith('/prototypes/')}
    links = [html.Div([
        html.H3(dcc.Link(p['title'], href=p['path']), id=p['module'].replace('pages.', '')),
        html.P(p['description'])
    ]) for p in tool_pages.values()]
    return html.Div([
        html.H2('Prototypes'),
        html.Div(links)
    ])
