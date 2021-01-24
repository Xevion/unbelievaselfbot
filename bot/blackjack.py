import re
from typing import Tuple, Optional, List, Union, Dict

from bot import exceptions


class Card(object):
    suits = {'h': 'Hearts', 's': 'Spades', 'c': 'Clubs', 'd': 'Diamonds'}
    symbols = {'10': 'Ten', '9': 'Nine', '8': 'Eight', '7': 'Seven', '6': 'Six', '5': 'Five', '4': 'Four', '3': 'Three',
               '2': 'Two', 'k': 'King', 'q': 'Queen', 'j': 'Jack', 'a': 'Ace'}

    def __init__(self, card: str) -> None:
        self.raw_card = card
        self.symbol, self.suit = self.parts()

    @property
    def value(self, safe: bool = True) -> int:
        """
        Attempts to determine the numerical value of the card.

        Aces and unknown cards will raise an exception, unless the safe boolean is set to False.
        """
        if self.isAce():
            if safe:
                raise exceptions.NoAceValue(
                    'The Ace has multiple values (1 and 11) in Blackjack. Special handling is required.')
            return 0

        if self.isFace():
            return 10

        numeric_match = re.match(r'^(\d{1,2})', self.raw_card)
        if numeric_match is not None:
            return int(numeric_match.group(1))

        if safe:
            raise exceptions.IndetermineValue('Could not determine the numeric value of this card.')
        return 0

    def isAce(self) -> bool:
        return self.symbol == 'a'

    def isNumerical(self) -> bool:
        return self.symbol.isnumeric()

    def isFace(self) -> bool:
        return self.symbol in ['q', 'k', 'j']

    def parts(self) -> Tuple[str, str]:
        """
        Separates the raw card identifier into it's symbol and suit.
        Handles aces, face cards and numerical cards with any of the four suites.
        """
        match = re.match(r'^(\d{1,2}|[aqkj])([cdhs])$', self.raw_card)
        return match.group(1), match.group(2)

    def __repr__(self) -> str:
        return f'Card({self.symbols[self.symbol]} of {self.suits[self.suit]})'


def generate_table_structure(filename: str, column_keys: List[str], row_keys: List[str]) -> Dict[Tuple[str, str], str]:
    data = {}
    with open(filename) as hard_file:
        raw_data = [list(line) for line in hard_file.read().split('\n')]
    for x, col_key in enumerate(column_keys):
        for y, row_key in enumerate(row_keys):
            data[(col_key, row_key)] = raw_data[y][x]
    return data


class Blackjack(object):
    # The row and column headers for the hair, soft and pair baseline tables.
    hard_column = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    hard_row = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5']
    soft_column = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    soft_row = ['A-9', 'A-8', 'A-7', 'A-6', 'A-5', 'A-4', 'A-3', 'A-2']
    pair_column = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    pair_row = ['A-A', 'T-T', '9-9', '8-8', '7-7', '6-6', '5-5', '4-4', '3-3', '2-2']

    hard_data = generate_table_structure('static/baseline_hard.dat', hard_column, hard_row)
    soft_data = generate_table_structure('static/baseline_soft.dat', soft_column, soft_row)
    pair_data = generate_table_structure('static/baseline_pairs.dat', pair_column, pair_row)

    HARD = 0
    SOFT = 1
    PAIR = 2

    @staticmethod
    def choose(options: Tuple[bool, bool, bool, bool], cards: Tuple[str, Optional[str], Tuple[int, bool]],
               dealer: Tuple[str, Optional[str], Tuple[int, bool]]) -> str:
        """With all information presented, calculates the final decision."""

    def get_ideal_choice(self, cards: List[Card],
                         dealer: Tuple[str, Optional[str], Tuple[int, bool]]) -> str:
        """Gets the ideal baseline strategy choice based on my cards and the bot's cards."""

    def options_convert(self, choice: str, options: Tuple[bool, bool, bool, bool]):
        """Converts the choice to the best possible choice based on the options given by the bot."""

    @classmethod
    def access(cls, table: Union[HARD, SOFT, PAIR], key: Tuple[str, str]) -> str:
        """
        Access table data given a column and row key.

        :param key:
        :param table:
        :return:
        """
        if table == cls.HARD: return cls.hard_data[key]
        if table == cls.SOFT: return cls.soft_data[key]
        if table == cls.PAIR: return cls.pair_data[key]
