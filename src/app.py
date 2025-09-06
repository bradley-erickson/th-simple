import dash
from dash import html
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from flask import send_from_directory, jsonify
import os
import uuid

if os.getenv('TH_DEPLOY'):
    print('Monkey patching for Gevent')
    from gevent import monkey
    monkey.patch_all()

load_dotenv()

from components import navbar, footer
from utils import cache

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
html2canvas = {'src': 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'}

launch_uid = uuid.uuid4()

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc_css,
        'https://use.fontawesome.com/releases/v6.7.2/css/all.css',
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
)
cache.cache.init_app(app.server)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="manifest" href="./assets/manifest.json" />
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1461880207794875" crossorigin="anonymous"></script>
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


@server.route('/ads.txt')
def serve_text_file():
    return send_from_directory(directory='assets', path='ads.txt')


@server.get('/health')
def check_health():
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True)
