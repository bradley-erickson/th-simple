import dash
from dash import html
import dash_bootstrap_components as dbc

from components import footer, patreon

dash.register_page(
    __name__,
    path='/about',
    title='About',
    description='Discover Trainer Hill: Your Premier Source for Pokémon TCG Analytics'
)

play_limitless_link = html.A('play.limitlesstcg', href='play.limitlesstcg.com')

faq = [
    {'q': 'What is Trainer Hill?',
     'a': 'Trainer Hill is your dedicated platform for in-depth competitive analysis of the Pokémon Trading Card '\
          'Game (TCG). Our aim is to provide players with the tools and insights they need to '\
          'make informed, strategic decisions in their gameplay and deck building.'},
    {'q': 'Where does the data come from?',
     'a': ['Online data is collected from the ', play_limitless_link,
           ' online tournament platform. ', 'Data from Majors tournaments is collected from both ',
           html.A('LimitlessTCG', href='www.limitlesstcg.com'), ' and ', html.A('PokeData', href='www.pokedata.ovh'),
           '.']},
    {'q': 'How are deck archetypes determined?',
     'a': ['The ', play_limitless_link, ' online tournament platform keeps an up-to-date ruleset that determines ',
           'the deck archetype based on cards played.']},
    {'q': 'I encountered a bug or I have an idea. What do I do?',
     'a': ['Submit a ', html.A('Feedback form', href='/feedback'), '.']},
    {'q': 'Who runs Trainer Hill?', 'a': "It's just me! My name is Brad and I'm a lifelong Pokémon fan."},
    {'q': 'How long has this website been online?',
     'a': 'Trainer Hill first went online in December 2020.'},
    {'q': 'How can I support the site?',
     'a': ['Become a member on ', html.A('Patreon', href=patreon.patreon_link, target='_blank'), ' or ',
           html.A('buy me a coffee', href=footer.bmc_link, target='_blank'), '.']}
]

layout = dbc.Container([
    html.H2('About Trainer Hill'),
    html.Div([
        html.Div([
            html.Strong(i['q']),
            html.P(i['a'])
        ]) for i in faq
    ]),
    html.Small('Please note: Trainer Hill is an independent entity and is not affiliated with The Pokémon '\
               'Company International (TPCi), Nintendo, Creatures, or Game Freak.')
])
