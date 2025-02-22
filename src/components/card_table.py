from dash import html, dcc
import dash_bootstrap_components as dbc
import math
import pandas as pd
import plotly.express as px

from utils import colors, images

color_breakdown = colors.blue
color_inclusion = colors.red
color_winrate = colors.green

def create_grid_item(card, total, game):
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
        color_discrete_sequence=[color_breakdown],
        labels=dict(count='', play_rate=''),
    )
    figure.update_traces(
        marker_line_color='black',
        marker_line_width=1
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
        linecolor='black'
    )
    figure.update_yaxes(
        showticklabels=False,
        title=None,
        range=[0, 1.4],
        showgrid=False
    )

    item = dbc.Col([
        html.Img(src=images.get_card_image(id, 'SM', game), className='w-100'),
        html.Div(
            dcc.Graph(
                figure=figure,
                config={'staticPlot': True},
                className='bg-white rounded h-100 w-100 bg-blur'
            ),
            className='position-absolute bottom-0 h-50 start-0 end-0 m-1'
        ),
        html.Div(
            dbc.Progress(
                value=play_rate*100, label=f'{play_rate:.1%}',
                class_name='w-100',
                color=color_inclusion
            ),
            className='position-absolute bottom-40 p-2 w-100'
        ),
        dbc.Badge(
            int(max_num),
            class_name='position-absolute top-0 end-0 m-2 mt-3 rounded-circle font-monospace border border-light',
        )
    ], className='position-relative', id=id, xs=4, sm=3, md=2, lg=2)
    return item

def create_grid_layout(cards, total, game):
    skeleton_count = sum(c['count'] for c in cards if c['skeleton'])
    row = dbc.Row([
        html.H5(['Skeleton', dbc.Badge(skeleton_count, className='ms-1')]),
        dbc.Row([create_grid_item(card, total, game) for card in cards if card['skeleton']], className='g-1 mb-1'),
        html.H5('Other cards'),
        dbc.Row([create_grid_item(card, total, game) for card in cards if not card['skeleton']], className='g-1')
    ])
    return row

def create_list_item(card, max_count, total, game):
    id = card['card_code']
    color = colors.red_gradient[math.floor(card['play_rate']*100)]

    hover_bars = [
        dbc.Label('Overall'),
        dbc.Progress(value=card['play_rate'], max=1, color=color_inclusion, label=f"{card['play_rate']:.1%}"),
    ]

    counts = [html.Td()]*max_count
    win_rates = [html.Td()]*max_count
    for count in sorted(card['counts'], key=lambda d: d['count']):
        c = count['count']
        c_value = count["decks"] / total
        c_color = colors.blue_gradient[math.floor(c_value * 100)]
        counts[c-1] = html.Td(
            html.Span(f'{c_value:.1%}', className='d-none d-md-inline'),
            style={'backgroundColor': c_color},
            className='text-end'
        )
        win_rate_value = count['win_rate']
        win_rates[c-1] = html.Td(
            html.Span(f'{win_rate_value:.1%}', className='d-none d-md-inline'),
            style={'backgroundColor': colors.green_gradient[math.floor(win_rate_value * 100)]},
            className='text-end')
        hover_bars.append(dbc.Label(f'{c} cop{"ies" if c > 1 else "y"}'))
        hover_bars.append(dbc.Progress(value=c_value, max=1, color=color_breakdown))
        hover_bars.append(dbc.Progress(value=win_rate_value, max=1, color=color_winrate))

    cells = [
        dbc.Popover(
            dbc.PopoverBody(dbc.Row([
                dbc.Col([
                    html.Img(src=images.get_card_image(id, 'SM', game), className='w-100'),
                    dbc.Badge('Overall play-rate %', color=color_inclusion),
                    dbc.Badge('Play-rate %', color=color_breakdown),
                    dbc.Badge('Win-rate %', color=color_winrate),
                ], width=5),
                dbc.Col(hover_bars, width=7)
            ])),
            target=id,
            trigger='hover legacy',
            placement='bottom'
        ),
        html.Td(f"{card['name']} {card['card_code']}", className='w-100'),
        html.Td(
            html.Span(f'{card["play_rate"]:.1%}'),
            style={'backgroundColor': color},
            className='text-end')
    ]
    cell_cutoff = 2 if game == 'POCKET' else 4
    cells.extend(counts[:cell_cutoff])
    cells.extend(win_rates[:cell_cutoff])
    row = html.Tr(cells, id=id)
    return row

def create_list_layout(cards, total, game):
    max_count = max(count['count'] for card in cards for count in card['counts'])
    skeleton_count = sum(c['count'] for c in cards if c['skeleton'])
    skeleton = []
    other = []
    for card in cards:
        if card['skeleton']:
            skeleton.append(create_list_item(card, max_count, total, game))
        else:
            other.append(create_list_item(card, max_count, total, game))

    count_cutoff = 2 if game == 'POCKET' else 4
    headers = [html.Th('Card'),
        html.Th('Play-rate %', colSpan=count_cutoff + 1, className='text-center small'),
        html.Th('Win-rate %', colSpan=count_cutoff, className='text-center small')]
    subheaders = [html.Th(), html.Th('Overall', className='small')] +\
        [html.Th(i, className='text-end small') for i in range(1, count_cutoff + 1)] +\
        [html.Th(i, className='text-end small') for i in range(1, count_cutoff + 1)]

    body = [html.Tr(html.Td(['Skeleton', dbc.Badge(skeleton_count, className='ms-1')]))] + skeleton + [html.Tr(html.Td('Other'))] + other

    table = dbc.Table([
        html.Thead([html.Tr(headers), html.Tr(subheaders)]),
        html.Tbody(body)
    ])
    return table

container_layout = {
    'grid': create_grid_layout,
    'list': create_list_layout
}
