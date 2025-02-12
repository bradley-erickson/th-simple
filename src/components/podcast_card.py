from dash import html
import dash_bootstrap_components as dbc


def create_podcast_card(pod):
    url = pod['link']
    large_card = dbc.Card(html.A([
        dbc.Row([
            dbc.Col(dbc.CardImg(
                src=pod['image'],
                class_name='img-fluid rounded-start ms-1 my-1'
            ), xs=2, md=3),
            dbc.Col(dbc.CardBody([
                html.H5(pod['title']),
                html.Div(pod['podcast_title'], className='text-muted'),
                html.Small(pod['published'].strftime('%a %b %D %Y at %H:%M %Z'), className='text-muted'),
            ], class_name='text-decoration-none'), xs=10, md=9)
        ], className='g-0 h-100 d-flex align-items-center')
    ], href=url, target='_blank', className='text-decoration-none'), class_name='h-100 d-none d-md-block')

    small_card = dbc.Card(html.A([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dbc.CardImg(
                    src=pod['image'],
                    class_name='img-fluid rounded-start'
                ), xs=2),
                dbc.Col([
                    html.Div(pod['podcast_title'], className='text-muted'),
                    html.Small(pod['published'].strftime('%a %b %D %Y at %H:%M %Z'), className='text-muted'),
                ], xs=10)
            ], className='g-2 h-100 d-flex align-items-center'),
            html.H5(pod['title'])
        ])
    ], href=url, target='_blank', className='text-decoration-none'), class_name='h-100 d-md-none')

    card = html.Div([
        large_card,
        small_card
    ], className='h-100')
    return card
