from dash import html, dcc

link_item = dcc.Link('Feedback Form', href='/feedback')

list_item = lambda page: html.Li([
    html.Strong('Need Assistance:'), ' If you encounter an issue or have suggestions, please submit a ',
    dcc.Link('Feedback Form', href=f'/feedback?page={page}', className='alert-link'), '.'
])
