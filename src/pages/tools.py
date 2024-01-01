import dash
from dash import html

dash.register_page(
    __name__,
    path='/tools',
    title='Tools',
    image='tools.png',
    description='Enhance your Pokémon TCG strategy with our suite of specialized tools. From creating custom tier lists to comparing decklists, our tools are designed to elevate your gameplay. Each tool offers unique insights and functionalities, making it easier to analyze, strategize, and refine your approach to the Pokémon Trading Card Game. Ideal for both casual players and competitive enthusiasts seeking an edge in their game.'
    # description='Enhance your Pokémon TCG strategy with our suite of specialized tools. From creating custom tier lists to comparing decklists and tracking game notes, our tools are designed to elevate your gameplay. Each tool offers unique insights and functionalities, making it easier to analyze, strategize, and refine your approach to the Pokémon Trading Card Game. Ideal for both casual players and competitive enthusiasts seeking an edge in their game.'
)

def layout():
    tool_pages = {page['title']: page for page in dash.page_registry.values() if page['path'].startswith('/tools/')}
    links = [html.Div([
        html.H3(html.A(p['title'], href=p['path'])),
        html.P(p['description'])
    ]) for p in tool_pages.values()]
    return html.Div([
        html.H2('Tools'),
        html.Div(links)
    ])
