from dash import html, Output, Input, callback
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt

from components import navbar, patreon

prefix = 'footer'

aff = 'TrainerHill'
tcg_player_link = f'https://tcgplayer.com/?utm_campaign=affiliate&utm_medium={aff}&utm_source={aff}'
bmc_link = 'https://www.buymeacoffee.com/trainerhill'

footer = dbc.Navbar(
    dbc.Container([
        dbc.NavLink(
            html.I(className='fab fa-bluesky fs-5', title='Follow us on Bluesky'),
            href='https://bsky.app/profile/trainerhill.com',
            target='_blank'
        ),
        dbc.NavLink(
            html.I(className='fab fa-twitter fs-5', title='Follow us on Twitter'),
            href='https://twitter.com/Trainer_Hill',
            target='_blank'
        ),
        dbc.NavLink(
            html.I(className='fab fa-discord fs-5', title='Join our Discord server'),
            href='https://discord.gg/tDwNSt6Z7w',
            target='_blank'
        ),
        dbc.NavLink(
            html.I(className='fab fa-patreon fs-5', title='Become a Patreon member'),
            href=patreon.patreon_link,
            target='_blank'
        ),
        dbc.NavLink(
            html.I(className='fas fa-mug-hot fs-5', title='Support the site'),
            href=bmc_link,
            target='_blank'
        ),
        dbc.NavLink(
            'About',
            href='/about'
        ),
        dbc.NavLink(
            'Feedback',
            href='/feedback'
        ),
    ], class_name='justify-content-start', fluid=True),
    class_name='footer',
    id=prefix
)

@callback(
    Output(prefix, 'color'),
    Output(prefix, 'dark'),
    Input(dbt.ThemeSwitchAIO.ids.switch(navbar.theme), 'value')
)
def update_navbar(value):
    if value:
        return 'dark', True
    return 'light', False
