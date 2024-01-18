from dash import html, Output, Input, State, callback, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt

from utils.images import logo_black_tunel, logo_white_tunel

prefix = 'navbar'
toggler = f'{prefix}-toggler'
collapse = f'{prefix}-collapse'
image = f'{prefix}-image'
theme = f'{prefix}-theme'

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
                            dbc.DropdownMenu(
                                [
                                    dbc.DropdownMenuItem('Battle Log', href='/tools/battle-log'),
                                    dbc.DropdownMenuItem('Deck Diff', href='/tools/deck-diff'),
                                    dbc.DropdownMenuItem('Podcast Hub', href='/tools/podcast-hub'),
                                    dbc.DropdownMenuItem('Tier List', href='/tools/tier-list'),
                                ],
                                label='Tools',
                                nav=True,
                                in_navbar=True,
                                class_name='me-1'
                            ),
                        ],
                        navbar=True,
                        class_name='d-none d-md-flex'
                    ),
                    dbc.Nav(
                        [
                            dbc.NavItem(html.Small('Analysis')),
                            dbc.NavItem(dbc.NavLink('Meta', href='/meta')),
                            dbc.NavItem(dbc.NavLink('Decklist', href='/decklist')),
                            dbc.NavItem(html.Small('Tools')),
                            dbc.NavItem(dbc.NavLink('Battle Log', href='/tools/battle-log')),
                            dbc.NavItem(dbc.NavLink('Deck Diff', href='/tools/deck-diff')),
                            dbc.NavItem(dbc.NavLink('Podcast Hub', href='/tools/podcast-hub')),
                            dbc.NavItem(dbc.NavLink('Tier List', href='/tools/tier-list')),
                        ],
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
