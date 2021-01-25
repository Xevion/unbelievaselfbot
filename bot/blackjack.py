import logging
import os
import re
from typing import Tuple, List, Dict

import discord

from bot import exceptions, constants

logger = logging.getLogger(__file__)
logger.setLevel(constants.LOGGING_LEVEL)


class Card(object):
    _suits = {'H': 'Hearts', 'S': 'Spades', 'C': 'Clubs', 'D': 'Diamonds'}
    _symbols = {'10': 'Ten', '9': 'Nine', '8': 'Eight', '7': 'Seven', '6': 'Six', '5': 'Five', '4': 'Four',
                '3': 'Three',
                '2': 'Two', 'k': 'King', 'q': 'Queen', 'j': 'Jack', 'a': 'Ace'}

    EMOTE_REGEX = re.compile(r'<:([A-z0-9]+):\d+>')
    VALUE_PATTERN = re.compile(r'Value: (?:Soft )?(\d+)')

    def __init__(self, card: str) -> None:
        if 4 <= len(card) <= 1:
            raise exceptions.InvalidCard(f'By length, {card} is invalid. Identifiers are 2 to 3 characters long.')

        self.raw_card = card
        self.symbol, self.suit = self.parts()

    @property
    def value(self, safe: bool = True, unsafe_default: int = 0) -> int:
        """
        Attempts to determine the numerical value of the card.

        Aces and unknown cards will raise an exception, unless the safe boolean is set to False.
        """
        if self.isAce():
            if safe:
                raise exceptions.NoAceValue(
                    'The Ace has multiple values (1 and 11) in Blackjack. Special handling is required.')
            return 0
        elif self.isFace():
            return 10
        elif self.isNumerical():
            return int(self.symbol)
        elif safe:
            raise exceptions.IndetermineValue('Could not determine the numeric value of this card.')
        return unsafe_default

    def isAce(self) -> bool:
        """Returns whether or not the card is a Ace card."""
        return self.symbol == 'a'

    def isNumerical(self) -> bool:
        """Returns whether or not the card is numerical (not face or ace)."""
        return self.symbol.isnumeric()

    def isFace(self) -> bool:
        """Returns whether or not the card is a face card (Queen, King, or Jack)"""
        return self.symbol in ['q', 'k', 'j']

    def parts(self) -> Tuple[str, str]:
        """
        Separates the raw card identifier into it's symbol and suit.
        Handles aces, face cards and numerical cards with any of the four suites.
        """
        match = re.match(r'^(\d{1,2}|[aqkj])([cdhs])$', self.raw_card, flags=re.IGNORECASE)
        return match.group(1), match.group(2)

    @property
    def table(self) -> str:
        """Gets the table key representation of this card. Dealer column, or (partial) Player Soft/Pair rows only."""
        if self.isAce(): return 'A'
        if self.isFace(): return 'T'
        if self.isNumerical(): return self.symbol
        return '?'

    @classmethod
    def parse_cards(cls, card_str: discord.embeds.EmbedProxy) -> Tuple[int, List['Card']]:
        """Given a EmbedProxy relating to a Blackjack Embed, finds a returns a list of Card objects and the value."""
        card_matches = re.finditer(cls.EMOTE_REGEX, card_str.value)
        value = re.search(cls.VALUE_PATTERN, card_str.value)

        cards = []
        for card in card_matches:
            identifier = card.group(1)
            if identifier != 'cardBack':
                cards.append(Card(identifier))

        return int(value.group(1)), cards

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return self.symbol == other.symbol
        return False

    def __repr__(self) -> str:
        return f'Card({self._symbols[self.symbol]} of {self._suits[self.suit]})'


def generate_table_structure(filename: str, column_keys: List[str], row_keys: List[str]) -> Dict[Tuple[str, str], str]:
    """
    Using a column and row header variable, create a dictionary representing the table.

    :param filename: The file in the static directory to read data from.
    :param column_keys: Keys in the column (y)
    :param row_keys: Keys in the row (x)
    :return: A dictionary with all keys as a tuple of the column and row key directing to the table's suggested play.
    """

    logger.debug(f'Generating table structure with {filename}')
    with open(os.path.join(constants.STATIC_DIR, filename)) as hard_file:
        raw_data = [list(line) for line in hard_file.read().split('\n') if len(line) > 0]

    data = {}
    # Iterate along the column keys and build the dictionary
    for x, col_key in enumerate(column_keys):
        for y, row_key in enumerate(row_keys):
            data[(row_key, col_key)] = raw_data[y][x]

    return data


class Blackjack(object):
    # The row and column headers for the hair, soft and pair baseline tables.
    __hard_column = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    __hard_row = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5']
    __soft_column = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    __soft_row = ['A-9', 'A-8', 'A-7', 'A-6', 'A-5', 'A-4', 'A-3', 'A-2']
    __pair_column = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    __pair_row = ['A-A', 'T-T', '9-9', '8-8', '7-7', '6-6', '5-5', '4-4', '3-3', '2-2']

    __letter_meanings = {'H': 'hit', 'S': 'stand', 'D': 'double down', 'P': 'split'}

    __hard_data = generate_table_structure('baseline_hard.dat', __hard_column, __hard_row)
    __soft_data = generate_table_structure('baseline_soft.dat', __soft_column, __soft_row)
    __pair_data = generate_table_structure('baseline_pairs.dat', __pair_column, __pair_row)

    HARD, SOFT, PAIR = 0, 1, 2

    @staticmethod
    def choose(options: constants.PlayOptions, cards: List[Card], dealer: Card) -> str:
        """With all information presented, calculates the final decision."""

        choice: str = 'S'  # Default is to stand
        usedDefault = True

        # Pair checking first
        if len(cards) == 2 and cards[0] == cards[1]:
            symbol = {cards[0].table}
            logger.debug(f'Pair of {cards[0]} found.')
            choice = Blackjack.access(Blackjack.PAIR, (f'{symbol}-{symbol}', dealer.table))
            usedDefault = False
        elif any(card.isAce() for card in cards):
            sum_value = sum(card.value for card in cards if not card.isAce())
            if 2 <= sum_value <= 9:
                choice = Blackjack.access(Blackjack.SOFT, (f'A-{sum_value}', dealer.table))
                usedDefault = False
            else:
                cards = ", ".join(card.symbol.upper() for card in cards)
                logger.error(f'Sum of cards was a Soft {sum_value} ({cards})')
        else:
            sum_value = sum(card.value for card in cards)
            if 5 <= sum_value <= 20:
                choice = Blackjack.access(Blackjack.HARD, (str(sum_value), dealer.table))
                usedDefault = False
            else:
                cards = ", ".join(card.symbol.upper() for card in cards)
                logger.error(f'Sum of cards was a Soft {sum_value} ({cards})')

        if usedDefault:
            logger.warning('No tables were accessed to make a choice. Defaulting to stand.')
        return Blackjack.convert_letter(choice)

    @classmethod
    def convert_letter(cls, letter: str) -> str:
        """Simple class method for returning the player response to the bot based on the letter given."""
        return Blackjack.__letter_meanings[letter]

    def options_convert(self, choice: str, options: constants.PlayOptions) -> str:
        """Converts the choice to the best possible choice based on the options given by the bot."""

        new_choice = None
        if choice == 'P':
            if not options.split:
                logger.warning(f'Poor options available for splitting. ({options})')
                new_choice = 'S'
        elif choice == 'D':
            if not options.double:
                logger.warning(f'Poor options available for doubling. ({options})')
                new_choice = 'H'
        elif choice == 'H':
            if not options.hit:
                logger.error(f'Hit option preferred but not possible? ({options})')
                new_choice = 'S'
        elif choice == 'S':
            if not options.stand:
                logger.error(f'Stand option preferred but not possible? ({options})')
                new_choice = 'H'

        if new_choice is not None:
            logger.info(
                f'Option verification yielded a different method than originally selected: {choice} -> {new_choice}')
            return new_choice
        return choice

    @classmethod
    def access(cls, table: int, key: Tuple[str, str]) -> str:
        """
        Access table data given a column and row key.

        :param key:
        :param table:
        :return:
        """
        if table == cls.HARD: return cls.__hard_data[key]
        if table == cls.SOFT: return cls.__soft_data[key]
        if table == cls.PAIR: return cls.__pair_data[key]
