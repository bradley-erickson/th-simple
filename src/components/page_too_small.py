from dash import html
import dash_bootstrap_components as dbc

alert = dbc.Alert(
    [
        html.I(className='fas fa-exclamation-triangle me-1'),
        'This page is best viewed on a larger screen.'
    ],
    color='warning',
    dismissable=True,
    is_open=True,
    class_name='my-1 d-md-none'
)