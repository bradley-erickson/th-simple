from utils import cards as _cards

def parse_decklist(l):
    deck = []
    if not l:
        return deck
    for c in l.split('\n'):
        if len(c.strip()) == 0:
            continue
        if not c[0].isdigit():
            continue
        c_split = c.split(' ')
        c_set = c_split[-2]
        c_num = c_split[-1]
        energy_check = c_set != 'Energy' and c_num not in _cards.ENERGY.values()
        c_set = c_set if energy_check else 'BRS'
        c_num = c_num if energy_check else c_split[2].replace('{', '').replace('}', '') if c_split[1] == 'Basic' else _cards.ENERGY[c_split[1]]
        card = {
            'card_code': f'{c_set}-{c_num.zfill(3) if energy_check else c_num}',
            'set': c_set,
            'number': c_num,
            'name': ' '.join(c_split[1:-2]),
            'count': int(c_split[0]),
        }
        card = _cards.get_card(card)
        deck.append(card)
    return deck
