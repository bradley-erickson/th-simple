from dash import html, dcc

link_item = dcc.Link('Feedback Form', href='/feedback')

list_item = html.Li([
    html.Strong('Need Assistance:'), ' If you encounter an issue or have suggestions, please submit a ',
    dcc.Link('Feedback Form', href='/feedback', className='alert-link'), '.'
])
