import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    path='/about',
    title='About',
    description='Discover Trainer Hill: Your Premier Source for Pokémon TCG Analytics'
)

layout = html.Div([
    html.H2('About'),
    html.P('Welcome to Trainer Hill, previously known as DinoData.app, your dedicated '\
           'platform for in-depth competitive analysis of the Pokémon Trading Card Game (TCG).'),
    html.P('In the realm of competitive e-sports, data analysis plays a crucial role in '\
           "informing players' strategies and decisions. Until recently, the Pokémon TCG "\
           'community lacked a centralized source for such analytical insights, leaving '\
           'players to conduct their own data research. The advent of play.limitlesstcg.com '\
           'in 2020 marked a turning point, vastly expanding the data available to players '\
           'and enthusiasts.'),
    html.P('Trainer Hill leverages this wealth of information to bring the Pokémon TCG '\
           'community the kind of data-driven analysis that has long been a staple in other '\
           'e-sports. Our aim is to provide players with the tools and insights they need to '\
           'make informed, strategic decisions in their gameplay and deck building.'),
    html.P("I'm Brad Erickson, also known as RaptorBrad, the founder and sole operator behind "\
           'Trainer Hill. What began as a small-scale analytics project born out of personal '\
           'interest has evolved into the comprehensive resource you see today. My passion for '\
           'the Pokémon TCG and data analytics drives this project, and I am thrilled to share '\
           'these insights with the community.'),
    html.P('Thank you for visiting Trainer Hill. Your support and enthusiasm make this journey worthwhile.'),
    html.P('Please note: Trainer Hill is an independent entity and is not affiliated with The Pokémon '\
           'Company International (TPCi), Nintendo, Creatures, or Game Freak.')
])
