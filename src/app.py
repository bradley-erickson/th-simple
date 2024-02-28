import dash
from dash import html, DiskcacheManager
import dash_bootstrap_components as dbc

from components import navbar, footer
from utils import cache

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
html2canvas = {'src': 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'}

import diskcache
_diskcache = diskcache.Cache("./.diskcache")
background_callback_manager = DiskcacheManager(_diskcache)

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc_css,
        dbc.icons.FONT_AWESOME,
        'https://epsi95.github.io/dash-draggable-css-scipt/dragula.css'
    ],
    external_scripts=[
        html2canvas,
        'https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.2/dragula.min.js',
        'https://epsi95.github.io/dash-draggable-css-scipt/script.js'
    ],
    meta_tags=[
        {
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1'
        }
    ],
    suppress_callback_exceptions=True,
    title='Trainer Hill',
    background_callback_manager=background_callback_manager
)
cache.cache.init_app(app.server)


def serve_layout():
    return html.Div(
        [
            navbar.create_navbar(),
            dbc.Alert([
                'This is a dev site, things may change. If you would like to see specific changes please fill out a ',
                html.A('Feedback Form', className='alert-link', href='/feedback')
            ], id='devsite-alert', color='warning', dismissable=True, persistence=True, persistence_type='local'),
            dbc.Container(
               html.Div(dash.page_container, className='my-1'),
               class_name='page-container',
               fluid=True
            ),
            footer.footer
        ],
        className='dbc app'
    )

app.layout = serve_layout
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
