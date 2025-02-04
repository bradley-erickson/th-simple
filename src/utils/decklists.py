import hashlib
from pokemontcgsdk import PokemonTcgException

import utils.cards


def _parse_decklist_str(l):
    deck = []
    unable_to_parse = []
    for c in l.split('\n'):
        if len(c.strip()) == 0:
            continue
        if not c[0].isdigit():
            continue
        c = c.replace('\t', ' ')
        c = c.removesuffix(' PH')
        c_split = c.split(' ')
        try:
            c_set = c_split[-2]
            c_num = c_split[-1]
        except IndexError:
            unable_to_parse.append(c)
            continue
        energy_check = c_set != 'Energy' and c_num not in utils.cards.ENERGY.values()
        c_set = c_set if energy_check else 'BRS'
        c_num = c_num if energy_check else c_split[2].replace('{', '').replace('}', '') if c_split[1] == 'Basic' else utils.cards.ENERGY[c_split[1]]
        card = {
            'card_code': f'{c_set}-{c_num.zfill(3) if energy_check else c_num}',
            'set': c_set,
            'number': c_num,
            'name': ' '.join(c_split[1:-2]),
            'count': int(c_split[0]),
        }
        try:
            card = utils.cards.get_card(card)
        except PokemonTcgException:
            unable_to_parse.append(c)
            continue
        deck.append(card)
    return deck, unable_to_parse


def _parse_decklist_dict_list(l):
    deck = []
    unable_to_parse = []
    for c in l:
        c_set = c['set']
        c_num = c['number']
        c_name = c['name'].split(' ')
        energy_check = c_set != 'Energy' and c_num not in utils.cards.ENERGY.values()
        c_set = c_set if energy_check else 'BRS'
        c_num = c_num if energy_check else c_name[1].replace('{', '').replace('}', '') if c_name[0] == 'Basic' else utils.cards.ENERGY[c_name[0]]
        card = {
            'card_code': f'{c_set}-{c_num.zfill(3) if energy_check else c_num}',
            'set': c_set,
            'number': c_num,
            'name': c['name'],
            'count': c['count'],
        }
        try:
            card = utils.cards.get_card(card)
        except PokemonTcgException:
            unable_to_parse.append(card)
            continue
        deck.append(card)
        pass
    return deck, unable_to_parse


def _hash_pokemon(card):
    attack_strings = [str(cls.__dict__) for cls in card.get('attacks', [])]
    ability_strings = [str(cls.__dict__) for cls in card.get('abilities', [])]
    combined = ''.join(attack_strings).encode('utf-8') + ''.join(ability_strings).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()


def parse_decklist(l):
    deck = []
    unable_to_parse = []
    if not l:
        return deck, unable_to_parse
    if isinstance(l, str):
        deck, unable_to_parse = _parse_decklist_str(l)
    elif isinstance(l, list) and isinstance(l[0], dict):
        deck, unable_to_parse = _parse_decklist_dict_list(l)
    else:
        print('Warning: unable to parse this type of decklist', type(l))

    for i, card in enumerate(deck):
        card_supertype = card.get('supertype', None)
        if not card_supertype:
            unique = card['card_code']
        elif card_supertype == 'Pokémon':
            unique = _hash_pokemon(card)
        elif card_supertype == 'Energy' or card_supertype == 'Trainer':
            unique = card['name']
        else:
            unique = i
        card['unique'] = unique

    return deck, unable_to_parse
