import dash
from dash import html
import dash_bootstrap_components as dbc

from components import navbar, footer
from utils import cache

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
html2canvas = {'src': 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.0/html2canvas.min.js'}

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
)
cache.cache.init_app(app.server)


def serve_layout():
    return html.Div(
        [
            navbar.navbar,
            dbc.Container(
               dash.page_container,
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
