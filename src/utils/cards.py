import th_helpers.utils.cards

from utils import cache


@cache.cache.memoize(timeout=604800)
def get_card(card):
    fetched_card = th_helpers.utils.cards.get_card(card['name'], card['set'], card['number'])
    card.update(fetched_card)
    return card
