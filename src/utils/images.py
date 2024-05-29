import base64

ptcg_card_url = 'https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci'
pokemon_url = 'https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/gen9'
pokemon_url = 'https://raw.githubusercontent.com/martimlobao/pokesprite/master/pokemon/regular'

logo_white_path = './assets/logo.png'
logo_white_tunel = base64.b64encode(open(logo_white_path, 'rb').read())

logo_black_path = './assets/logo_black.png'
logo_black_tunel = base64.b64encode(open(logo_black_path, 'rb').read())

pokemon_mapping = {
    'ogerpon': 'ogerpon-teal-mask',
    'squawkabilly': 'squawkabilly-green',
    'regieleki-a': 'regieleki',
    'ogerpon-cornerstone': 'ogerpon-cornerstone-mask',
}


def get_pokemon_icon(pokemon):
    if not pokemon:
        return ''
    if pokemon == 'substitute':
        source = '/assets/substitute.png'
    else:
        mon = pokemon_mapping[pokemon] if pokemon in pokemon_mapping else pokemon
        source = f'{pokemon_url}/{mon}.png'
    return source


def get_card_image(card_code, size):
    if not card_code:
        return ''
    card_code = card_code.replace('PR-SW', 'SSP')
    card_code = card_code.replace('PR-SV', 'SVP')
    set_code, number = card_code.split('-', 1)
    source = f'{ptcg_card_url}/{set_code}/{set_code}_{number}_R_EN_{size}.png'
    return source
