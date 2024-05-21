import dash
from dash import html, dcc

dash.register_page(
    __name__,
    path='/prototypes',
    title='Prototypes',
)

external_tools = [{
    'title': 'City League Analysis',
    'path': 'https://city.trainerhill.com',
    'module': 'external', 'external': True,
    'description': 'Check out card inclusion percentages for Japanese City Leagues.'
}]

def layout():
    tool_pages = {page['title']: page for page in dash.page_registry.values() if page['path'].startswith('/prototypes/')}
    for tool in external_tools:
        tool_pages[tool['title']] = tool
    links = [html.Div([
        html.H3(dcc.Link(
            html.Span([p['title'], html.I(className='fas fa-up-right-from-square ms-1') if p.get('external', False) else '']),
            href=p['path'], target='_blank' if p.get('external', False) else '_self'
        ), id=p['module'].replace('pages.', '')),
        html.P(p['description'])
    ]) for p in tool_pages.values()]
    return html.Div([
        html.H2('Prototypes'),
        html.Div(links)
    ])
