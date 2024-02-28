from dash import dcc

def create_placement_dropdown(id, placement, className=''):
    return dcc.Dropdown(
        options=[
            {'label': 'Winner', 'value': 1},
            {'label': 'Finals', 'value': 2},
            {'label': 'Top 4', 'value': 4},
            {'label': 'Top 8', 'value': 8},
            {'label': 'Top 16', 'value': 16},
            {'label': 'Top 32', 'value': 32},
            {'label': 'Top 64', 'value': 64},
            {'label': 'All', 'value': 10_000},
            {'label': 'Upper 5%', 'value': 0.05},
            {'label': 'Upper 10%', 'value': 0.1},
            {'label': 'Upper 25%', 'value': 0.25},
            {'label': 'Upper 50%', 'value': 0.5}
        ], id=id, value=placement, className=className
    )
