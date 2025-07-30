import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

import components.power_creep

# TODO
description = 'Something about power creep'

# dash.register_page(
#     __name__,
#     path='/power-creep',
#     title='Power Creep',
#     description=description
# )

# DOM ids
_prefix = 'home'
_hp_stage_era_line = f'{_prefix}-hp-stage-era-line'


def layout():

    cont = html.Div([
        html.H2('Power Creep Analysis'),
        # dcc.Graph(id=_hp_stage_era_line, figure=components.power_creep.hp_by_stage_by_era())
    ], id=_prefix)
    return cont
