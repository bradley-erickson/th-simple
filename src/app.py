import dash
from dash import html, DiskcacheManager, CeleryManager
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

from components import navbar, footer
from utils import cache

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
html2canvas = {'src': 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'}

launch_uid = uuid.uuid4()

if 'REDIS_URL' in os.environ:
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app, cache_by=[lambda: launch_uid], expire=1800)
    celery_app.conf.broker_connection_retry_on_startup = True
else:
    background_callback_manager = None

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
        },
        {
            'name': 'google-adsense-account',
            'content': 'ca-pub-1461880207794875'
        }
    ],
    suppress_callback_exceptions=True,
    title='Trainer Hill',
    background_callback_manager=background_callback_manager
)
cache.cache.init_app(app.server)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="manifest" href="./assets/manifest.json" />
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def serve_layout():
    return html.Div(
        [
            navbar.create_navbar(),
            # dbc.Alert([
            #     'This is a dev site, things may change. If you would like to see specific changes please fill out a ',
            #     html.A('Feedback Form', className='alert-link', href='/feedback')
            # ], id='devsite-alert', color='warning', dismissable=True, persistence=True, persistence_type='local'),
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
