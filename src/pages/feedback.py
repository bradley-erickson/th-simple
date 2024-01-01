import dash
from dash import html, callback, clientside_callback, ClientsideFunction, Output, Input, State, exceptions, no_update
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
comments = f'{prefix}-comments'
contact_method = f'{prefix}-contact-method'
contact_user = f'{prefix}-contact-user'
submit = f'{prefix}-submit'
webhook_url = os.environ['FEEDBACK_URL']


layout = html.Div([
    html.H2('Feedback'),
    html.Strong('We value your feedback!'),
    html.P("We'd love to hear your thoughts about our site. "\
           "Whether it's a suggestion, a bug, or just a quick "\
           "comment, your feedback is crucial in helping us improve.\n"\
           "If you wish to be contacted, leave your Twitter or Discord "\
           "so we can follow up. Thanks for helping us make our website "\
           "better for everyone."),
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
            dbc.Label('Comments'),
            dbc.Textarea(
                id=comments,
                value='',
                required=True
            )
        ]),
        html.Div([
            dbc.Label('Contact'),
            dbc.Row([
                dbc.Col(dbc.Select(
                    ['Twitter', 'Discord'],
                    placeholder='Preference',
                    id=contact_method,
                ),xs=6, sm=5, md=4, lg=3, xl=2),
                dbc.Col(dbc.Input(
                    placeholder='Contact',
                    id=contact_user,
                    class_name='inputgroup-input-fix'
                ),xs=6, sm=7, md=8, lg=9, xl=10)
            ])
        ]),
        dbc.Button('Submit', id=submit, type='submit', disabled=True, class_name='mt-1'),
    ])
])

clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='update_feedback_submit_disabled'),
    Output(submit, 'disabled'),
    Input(comments, 'value')
)

@callback(
    Output(alert, 'is_open'),
    Output(alert, 'children'),
    Output(alert, 'color'),
    Output(reason, 'value'),
    Output(comments, 'value'),
    Output(contact_method, 'value'),
    Output(contact_user, 'vallue'),
    Input(submit, 'n_clicks'),
    State(reason, 'value'),
    State(comments, 'value'),
    State(contact_method, 'value'),
    State(contact_user, 'vallue'),
)
def submit_form(clicks, r, c, cm, cu):
    if clicks is None:
        raise exceptions.PreventUpdate
    hook = discord.SyncWebhook.from_url(webhook_url)
    content = f'**Reason**: {r}\n'\
              f'**Comments**: {c}\n'\
              f'**Contact method**: {cm}\n'\
              f'**Contact username**: {cu}\n'
    sent = hook.send(content, wait=True)
    if sent is not None:
        return True, 'Submitted', 'success', None, '', None, ''
    return True, 'Error occured, try again later', 'danger', no_update, no_update, no_update, no_update
