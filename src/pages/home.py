import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

description = 'Discover Trainer Hill: The ultimate Pokémon '\
    'TCG analytics platform. Dive into meta analysis, deck '\
    'insights, and unique strategy tools for players.'

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Trainer Hill',
    description=description
)


def create_card(c):
    card = dbc.Card([
        dbc.CardImg(src=f'/assets/{c["image"]}'),
        dbc.CardImgOverlay(dcc.Link(dbc.CardBody([
            html.H3(c['title']),
            c['children'],
        ]), href=c['link']))
    ], color='light', className='home-card')
    return dbc.Col(card, md=6, lg=5, xl=4)


cards = [
    {'title': 'Meta Overview', 'link': '/meta', 'image': 'meta-analysis.png',
     'children': html.P('Unlock the secrets of the Pokémon TCG meta - Top 8 insights, matchup analysis, and more.')},
    {'title': 'Decklists Deep Dive', 'link': '/decklist', 'image': 'decklist-analysis.png',
     'children': html.P('Explore card breakdowns, usage trends, and matchup data for your favorite Pokémon TCG archetypes.')},
]

def create_tool(title, t):
    tool = dcc.Link(dbc.Card([
        html.H3(className=f'fas {t["icon"]}'),
        html.Div(title, className='text-')
    ], body=True, class_name='home-card text-center'), href=t['href'], className='text-decoration-none')
    return dbc.Col(tool, sm=6, md=4, xl=3)

def layout():
    main_pages = dbc.Row([
        create_card(c) for c in cards
    ], justify='around', class_name='g-1')
    tool_pages = {page['title']: {'href': page['path'], 'icon': page['icon']} for page in dash.page_registry.values() if page['path'].startswith('/tools/')}
    sorted_tools = sorted(tool_pages.keys())
    tools = dbc.Row([
        create_tool(k, tool_pages[k]) for k in sorted_tools
    ], justify='around', class_name='gy-2 mt-1')
    return dbc.Container([
        main_pages,
        tools
    ])
