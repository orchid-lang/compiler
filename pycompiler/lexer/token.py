from util import util
from lexer.token_type import Token_type
from util.log_level import Log_level

class Token:
    def __init__(self, word, type=Token_type.NONE):
        util.logger.log(f"Initializing new Token ('{word}', {type.name})", Log_level.DEBUG)
        self.__type = type
        self.__word = word

    def word_is(self, check):
        return self.__word == check
    