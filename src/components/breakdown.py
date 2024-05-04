from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import plotly.express as px


dbt.load_figure_template(['flatly', 'darkly'])


def create_deck_delta(d):
    if d > 0:
        return html.I(className='fas fa-arrow-trend-up text-success', title='Trending upward')
    elif d < 0:
        return html.I(className='fas fa-arrow-trend-down text-danger', title='Trending downward')
    return None


def create_list_label(d, max_num, i, placing, key):
    href = d.get('href', None)
    if href is not None and placing is not None and placing != 10_000:
        href += f'&placement={placing}'
    return html.Tr([
            html.Td(f'{i+1}.', className='text-center'),
            html.Td(create_deck_delta(d.get('delta', 0))),
            html.Td(
                dcc.Link(d['label'], href=href) if href is not None else d['label'],
                className='breakdown-deck-label'
            ),
            html.Td(f'{d[key]:.1%}' if key == 'percent' else d[key], className='text-end'),
            html.Td(dbc.Progress(value=d[key], max=max_num, class_name='bg-transparent'), className='w-100 d-none d-lg-table-cell')
        ], className=f'deck-row {"" if i < 8 else "d-none d-md-table-row"}')

def create_ordered_list(l, placing=None, key='percent'):
    max_num = max((d[key] for d in l), default=0)
    return dbc.Table(html.Tbody([
        create_list_label(d, max_num, i, placing, key) for i, d in enumerate(l)
    ]))


def create_pie_chart(l, theme):
    fig = px.pie(
        values=[d['count'] for d in l],
        names=[d['name'] for d in l],
        template='darkly' if theme else 'flatly'
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend=dict(
            x=0.5, y=-0.3, xanchor='center',
            yanchor='top', orientation='h'
        ),
        margin=dict(l=0, r=0),
        autosize=True
    )
    return dcc.Graph(figure=fig, className='h-100')
