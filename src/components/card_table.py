from dash import html, dcc
import dash_bootstrap_components as dbc
import math
import pandas as pd
import plotly.express as px

from utils import colors, images


def create_grid_item(card, total):
    id = card['card_code']
    play_rate = sum(x['decks'] for x in card.get('counts')) / total

    df = pd.DataFrame(
        data={
            'count': [c['count'] for c in card.get('counts')],
            'play_rate': [c['decks']/total for c in card.get('counts')]
        }
    )
    max_num = df.loc[df.play_rate.idxmax()]['count']
    df = df[df['count'] > 0]
    df.dropna(inplace=True)

    figure = px.bar(
        df, x='count', y='play_rate',
        color_discrete_sequence=[colors.green],
        labels=dict(count='', play_rate=''),
    )
    figure.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, b=0, t=0),
    )
    figure.update_xaxes(
        showgrid=False,
        title=None,
        type='category',
    )
    figure.update_yaxes(
        showticklabels=False,
        title=None,
        range=[0, 1.2],
        showgrid=False
    )

    item = dbc.Col([
        html.Img(src=images.get_card_image(id, 'SM'), className='w-100'),
        html.Div(
            dcc.Graph(
                figure=figure,
                config={'staticPlot': True},
                className='bg-light rounded h-100 w-100 bg-blur'
            ),
            className='position-absolute bottom-0 h-50 start-0 end-0 m-1'
        ),
        html.Div(
            dbc.Progress(
                value=play_rate*100, label=f'{play_rate:.1%}',
                class_name='w-100',
                color=colors.green
            ),
            className='position-absolute bottom-40 p-2 w-100'
        ),
        dbc.Badge(
            int(max_num),
            class_name='position-absolute top-0 end-0 m-2 mt-3 rounded-circle font-monospace border border-light',
        )
    ], className='position-relative', id=id, xs=4, sm=3, md=2, lg=2, xxl=1)
    return item

def create_grid_layout(cards, total):
    row = dbc.Row([
        create_grid_item(card, total) for card in cards
    ], className='g-1')
    return row

def create_list_item(card, max_count, total):
    id = card['card_code']
    color = colors.inclusion_bar[math.floor(card['play_rate']*100)]

    hover_bars = [
        dbc.Label('Overall'),
        dbc.Progress(value=card['play_rate'], max=1, color=colors.green),
    ]

    counts = [html.Td()]*max_count
    for count in sorted(card['counts'], key=lambda d: d['count']):
        c = count['count']
        c_value = count["decks"] / total
        c_color = colors.inclusion_bar[math.floor(c_value * 100)]
        counts[c-1] = html.Td(
            html.Span(f'{c_value:.1%}', className='d-none d-md-inline'),
            style={'backgroundColor': c_color},
            className='text-end'
        )
        hover_bars.append(dbc.Label(f'{c} cop{"ies" if c > 1 else "y"}'))
        hover_bars.append(dbc.Progress(value=c_value, max=1, color=colors.green))

    cells = [
        dbc.Popover(
            dbc.PopoverBody(dbc.Row([
                dbc.Col(
                    html.Img(src=images.get_card_image(id, 'SM'), className='w-100'),
                    width=6
                ),
                dbc.Col(hover_bars)
            ])),
            target=id,
            trigger='hover',
            placement='bottom'
        ),
        html.Td(f"{card['name']} {card['card_code']}", className='w-100'),
        html.Td(
            html.Span(f'{card["play_rate"]:.1%}', className='d-none d-md-inline'),
            style={'backgroundColor': color},
            className='text-end')
    ]
    cells.extend(counts[:4])
    row = html.Tr(cells, id=id)
    return row

def create_list_layout(cards, total):
    max_count = max(count['count'] for card in cards for count in card['counts'])
    body = []
    for card in cards:
        body.append(create_list_item(card, max_count, total))

    headers = [html.Th('Card'), html.Th('Overall')] + [html.Th(i, className='text-end') for i in range(1, 5)]

    table = dbc.Table([
        html.Thead(html.Tr(headers)),
        html.Tbody(body)
    ])
    return table

container_layout = {
    'grid': create_grid_layout,
    'list': create_list_layout
}