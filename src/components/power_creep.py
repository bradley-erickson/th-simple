import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import utils.colors

# Load in Power creep data
def _read_in_data():
    cwd = os.getcwd()
    data_in_path = os.path.join(cwd, 'assets', 'power_creep_data.csv')
    df = pd.read_csv(data_in_path)
    df.loc[df['set_block'] == 'HeartGold & SoulSilver', 'set_block'] = 'HG & SS'
    gb = df.groupby(['set_id', 'category', 'set_block', 'set_release']).agg({'hp': 'mean'}).reset_index()
    gb.sort_values(by='set_release', inplace=True)
    return gb


# _power_creep_df = _read_in_data()


def hp_by_stage_by_era():
    df = _power_creep_df.loc[_power_creep_df['category'].isin(['Basic', 'Stage 1', 'Stage 2'])]
    fig = go.Figure()
    for x in _power_creep_df['set_block'].unique():
        filt = _power_creep_df.loc[_power_creep_df['set_block'] == x]
        for stage in ['Basic', 'Stage 1', 'Stage 2']:
            category_filter = filt.loc[filt['category'] == stage]
            fig.add_trace(go.Scatter(x=category_filter['set_release'], y=category_filter['hp'], name=None,
                                mode='lines', line=dict(color='darkgray')))
        min_date = filt['set_release'].min()
        max_date = filt['set_release'].max()
        fig.add_vrect(x0=min_date, x1=max_date, 
                fillcolor=utils.colors.ERAS_COLORS[x], opacity=0.2, layer="below", 
                line_width=0, annotation_text=filt['set_block'].iloc[0], annotation_position="bottom right")

    df['set_release'] = pd.to_datetime(df['set_release'], format='%Y-%m-%d')
    by_block = df.groupby(['category', 'set_block']).agg(
        mean_hp=('hp', 'mean'),
        mean_set_release=('set_release', 'mean'),
        min_set_release=('set_release', 'min'),
        max_set_release=('set_release', 'max')
    ).reset_index()
    by_block.sort_values(by='mean_set_release', inplace=True)
    for stage in ['Basic', 'Stage 1', 'Stage 2']:
        category_filter = by_block.loc[by_block['category'] == stage]
        fig.add_trace(go.Scatter(x=category_filter['mean_set_release'], y=category_filter['mean_hp'], name=stage,
                            mode='lines', line=dict(color='gray', width=3)))
        fig.add_annotation(x=category_filter['mean_set_release'].iloc[-1], y=category_filter['mean_hp'].iloc[-1],
                        text=stage, showarrow=False, font=dict(size=24), yshift=20)
    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            tickmode='linear',  # Set tickmode to linear for regular intervals
            tick0=df['set_release'].min(),  # Starting tick
            dtick='M36',  # Display every 12 months (every year)
            tickformat='%Y'  # Show only the year
        ),
        yaxis=dict(
            range=[0, df['hp'].max()]
        )
    )
    return fig
