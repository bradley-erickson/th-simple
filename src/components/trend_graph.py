from dash import dcc
import plotly.express as px


def create_trend_graph(df):
    date_range = [df.date.min(), df.date.max()]
    fig = px.line(
        df, x='date', y='percent', color='card_count',
        range_y=[-0.06, df['percent'].max() + 0.06],
        range_x=date_range,
        custom_data=['card_count', 'counts'],
        labels=dict(date='', percent='% of decks', card_count='Card Count'),
    )
    fig.update_traces(
        hovertemplate='%{x}' +
                      '<br>%{customdata[0]} cards' +
                      '<br>%{y:.1%} decks' +
                      '<br>%{customdata[1]} total decks<extra></extra>'
    )
    fig.update_layout(
        legend=dict(
            yanchor="bottom",
            y=1,
            xanchor="left",
            x=1
        )
    )
    return dcc.Graph(figure=fig)
