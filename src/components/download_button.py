from dash import html, clientside_callback, ClientsideFunction, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import uuid

class DownloadImageAIO(html.Div):

    class ids:
        button = lambda aio_id: {
            'component': 'DownloadImageAIO',
            'subcomponent': 'button',
            'aio_id': aio_id
        }
        dom_id = lambda aio_id: {
            'component': 'DownloadImageAIO',
            'subcomponent': 'dom_id',
            'aio_id': aio_id
        }
        dummy = lambda aio_id: {
            'component': 'DownloadImageAIO',
            'subcomponent': 'dummy',
            'aio_id': aio_id
        }
    ids = ids

    def __init__(
        self,
        dom_id=None,
        aio_id=None,
        className=''
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        
        button = [
            dbc.Button(
                html.I(className='fas fa-download', title='Download image (png)'),
                id=self.ids.button(aio_id),
                n_clicks=0
            ),
            dbc.Input(id=self.ids.dom_id(aio_id), value=dom_id, class_name='d-none'),
            html.Div(id=self.ids.dummy(aio_id))
        ]
        super().__init__(button, className=className)

    clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='download_dom_as_image'),
        Output(ids.dummy(MATCH), 'className'),
        Input(ids.button(MATCH), 'n_clicks'),
        State(ids.dom_id(MATCH), 'value'),
        State(dbt.ThemeSwitchAIO.ids.switch('navbar-theme'), 'value')
    )
        