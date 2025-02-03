import dash
from dash import html, dcc, callback, clientside_callback, ClientsideFunction, Output, Input, State, exceptions, no_update
import dash_bootstrap_components as dbc
import discord
import os
from dotenv import load_dotenv

load_dotenv()


dash.register_page(
    __name__,
    path='/feedback',
    title='Feedback',
    description='Share your Thoughts: Help us improve Trainer Hill by submitting your ideas, reporting bugs, or providing feedback. Your input is invaluable in enhancing our Pokémon TCG analytics platform.'
)

prefix = 'feedback'
alert = f'{prefix}-alert'
reason = f'{prefix}-reason'
relevant_page = f'{prefix}-page'
comments = f'{prefix}-comments'
comments_message = f'{prefix}-comments-message'
contact_method = f'{prefix}-contact-method'
contact_user = f'{prefix}-contact-user'
contact_message = f'{prefix}-contact-message'
submit = f'{prefix}-submit'
webhook_url = os.environ['FEEDBACK_URL']

feedback_text = "We'd love to hear your thoughts about our site. Whether it's a suggestion, a bug, or just a quick comment, your feedback is crucial in helping us improve. If you wish to be contacted, leave your contact information so we can follow up. Thanks for helping us make our website better for everyone."


layout = html.Div([
    html.H2('Feedback'),
    html.Strong('We value your feedback!'),
    html.P(feedback_text),
    dbc.Alert(id=alert, dismissable=True, duration=5_000, is_open=False),
    dbc.Form([
        html.Div([
            dbc.Label('Reason'),
            dbc.RadioItems(
                ['Website issue', 'New feature suggestion', 'General comment'],
                id=reason
            )
        ]),
        html.Div([
            dbc.Label('Relevant Page'),
            dcc.Dropdown(
                ['None', 'Meta Analysis', 'Decklist Analysis', 'Badge Maker',
                 'Battle Journal', 'Deck Diff Table Compare', 'Deck Diff Venn Diagram',
                 'Podcast Hub', 'Prize Checker', 'Tier List Creator'
                ],
                value='None',
                id=relevant_page,
                clearable=False
            )
        ]),
        html.Div([
            dbc.Label('Comments'),
            dbc.Textarea(
                id=comments,
                value='',
                required=True,
                placeholder='Please describe your feedback in detail...'
            ),
            dbc.FormText('Responses must be a minimum of 10 characters.', color='muted', id=comments_message)
        ]),
        html.Div([
            dbc.Label('Contact'),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    ['None', 'Twitter', 'Bluesky', 'Discord', 'Email'],
                    placeholder='Preference',
                    value='None',
                    id=contact_method,
                    clearable=False
                ),xs=6, sm=5, md=4, lg=3, xl=2),
                dbc.Col(dbc.Input(
                    placeholder='Contact',
                    id=contact_user,
                    class_name='inputgroup-input-fix',
                    value=''
                ),xs=6, sm=7, md=8, lg=9, xl=10)
            ]),
            dbc.FormText('Please provide a username to contact.', color='muted', id=contact_message)
        ]),
        dbc.Button('Submit', id=submit, type='submit', disabled=True, class_name='mt-1'),
    ])
])

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='update_feedback_submit_disabled'),
    Output(submit, 'disabled'),
    Output(comments_message, 'className'),
    Output(contact_message, 'className'),
    Input(comments, 'value'),
    Input(contact_method, 'value'),
    Input(contact_user, 'value')
)

@callback(
    Output(alert, 'is_open'),
    Output(alert, 'children'),
    Output(alert, 'color'),
    Output(reason, 'value'),
    Output(relevant_page, 'value'),
    Output(comments, 'value'),
    Output(contact_method, 'value'),
    Output(contact_user, 'value'),
    Input(submit, 'n_clicks'),
    State(reason, 'value'),
    State(relevant_page, 'value'),
    State(comments, 'value'),
    State(contact_method, 'value'),
    State(contact_user, 'value'),
)
def submit_form(clicks, r, p, c, cm, cu):
    if clicks is None:
        raise exceptions.PreventUpdate
    hook = discord.SyncWebhook.from_url(webhook_url)
    content = f'**Reason**: {r}\n'\
              f'**Page**: {p}\n'\
              f'**Comments**: {c}\n'\
              f'**Contact method**: {cm}\n'\
              f'**Contact username**: {cu}\n'
    sent = hook.send(content, wait=True)
    if sent is not None:
        return True, 'Submitted', 'success', None, 'None', '', None, ''
    return True, 'Error occured, try again later', 'danger', no_update, no_update, no_update, no_update, no_update
