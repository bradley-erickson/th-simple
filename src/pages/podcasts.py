import dash
from dash import html, callback, Output, Input
import dash_bootstrap_components as dbc

from components import feedback_link
import components.podcast_card
import utils.podcasts

description = 'Stay tuned with our Pokémon TCG Podcast Hub: Latest episodes from top shows. Dive into insightful discussions for TCG enthusiasts.'

page_title = 'Podcast Hub'
page_icon = 'fa-podcast'

dash.register_page(
    __name__,
    path='/tools/podcast-hub',
    title=page_title,
    icon=page_icon,
    image='tools.png',
    description=description
)

prefix = 'podcasts'
container = f'{prefix}-container'


def layout():
    cont = html.Div([
        html.H2([html.I(className=f'fas {page_icon} me-1'), page_title]),
        dbc.Spinner(id=container),
        html.Div([
            'If we are ',
            html.Strong('missing'),
            ' a podcast, please submit a ',
            feedback_link.link_item,
            " with the podcast's name and we'll get it added!"
        ])
    ])
    return cont


@callback(
    Output(container, 'children'),
    Input(container, 'className')
)
def update_podcasts(_):
    episodes = utils.podcasts.fetch_latest_episodes()
    return dbc.Row([
        dbc.Col(
            components.podcast_card.create_podcast_card(pod),
            md=6, xxl=4,
            class_name='align-self-stretch'
        ) for pod in episodes
    ], class_name='g-1')
