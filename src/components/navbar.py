import dash
from dash import html, dcc, Output, Input, State, callback, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt

from utils.images import logo_black_tunel, logo_white_tunel

prefix = 'navbar'
toggler = f'{prefix}-toggler'
collapse = f'{prefix}-collapse'
image = f'{prefix}-image'
theme = f'{prefix}-theme'
popover = f'{prefix}-popover'

def create_navbar():
    tool_pages = {page['title']: page['path'] for page in dash.page_registry.values() if page['path'].startswith('/tools/')}
    sorted_tools = sorted(tool_pages.keys())
    small_nav_links = [
        dbc.NavItem(html.Small('Analysis')),
        dbc.NavItem(dbc.NavLink('Meta', href='/meta')),
        dbc.NavItem(dbc.NavLink('Decklist', href='/decklist')),
        dbc.NavItem(html.Small('Tools'))
    ]
    small_nav_links.extend([
        dbc.NavItem(dbc.NavLink(k, href=tool_pages[k])) for k in sorted_tools
    ])
    navbar = dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(
                    html.Img(
                        height='40px',
                        id=image
                    ),
                    href='/'
                ),
                dbc.NavbarToggler(id=toggler),
                dbc.Collapse(
                    [
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink('Meta', href='/meta')),
                                dbc.NavItem(dbc.NavLink('Decklist', href='/decklist')),
                                dbc.NavItem(dbc.NavLink('Tools', href='/tools'), id=popover),
                                dbc.Popover(dbc.Nav([
                                    dcc.Link(k, href=tool_pages[k], className='m-1 d-block') for k in sorted_tools
                                ], navbar=True), target=popover, trigger='hover', body=True, placement='bottom-start')
                            ],
                            navbar=True,
                            class_name='d-none d-md-flex'
                        ),
                        dbc.Nav(
                            small_nav_links,
                            navbar=True,
                            class_name='d-flex d-md-none'
                        ),
                        html.Div(
                            dbt.ThemeSwitchAIO(
                                aio_id=theme,
                                themes=[dbc.themes.DARKLY, dbc.themes.FLATLY],
                                switch_props={'value': False, 'persistence': True},
                                icons={'left': 'fa fa-sun', 'right': 'fa fa-moon'}
                            ), className='ms-auto d-flex'
                        )
                    ],
                    id=collapse,
                    navbar=True
                )
            ],
            fluid=True
        ),
        id=prefix
    )
    return navbar

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='toggle_with_button'),
    Output(collapse, 'is_open'),
    Input(toggler, 'n_clicks'),
    State(collapse, 'is_open')
)

@callback(
    Output(prefix, 'color'),
    Output(prefix, 'dark'),
    Output(image, 'src'),
    Input(dbt.ThemeSwitchAIO.ids.switch(theme), 'value')
)
def update_navbar(value):
    if value:
        return 'dark', True, 'data:image/png;base64,{}'.format(logo_white_tunel.decode())
    return 'light', False, 'data:image/png;base64,{}'.format(logo_black_tunel.decode())
