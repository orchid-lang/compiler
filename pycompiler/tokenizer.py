import util
import config
from log_level import Log_level
from scanner import Scanner
from token import Token
from token_type import Token_type

class Tokenizer:
    def __init__(self, text):
        util.logger.log(f"Initializing new Tokenizer", Log_level.DEBUG)
        self.__scanner = Scanner(text)
        self.__tokens = []
        self.__word = ""

    def __reset_word(self):
        self.__word = ""

    def __new_token(self, type):
        self.__tokens.append(Token(self.__word, type))

    def __read_keyword(self):
        if not self.__scanner.current_char().isalpha(): return

        self.__word += self.__scanner.current_char()
        while not self.__scanner.current_char().isspace() and self.__scanner.current_char() not in config.operators:
            self.__word += self.__scanner.next()

        if self.__word not in config.keywords: return

        if self.__word == "then":
            self.__tokens += config.then_expands_to
        else:
            self.__new_token(Token_type.KEYWORD)

        self.__reset_word()

    def __read_operator(self):
        if self.__scanner.current_char() not in config.operators: return

        self.__word += self.__scanner.current_char()
        while self.__scanner.current_char() in config.operators:
            self.__word += self.__scanner.next()

        self.__new_token(Token_type.OPERATOR)
        self.__reset_word()

    def __read_string_literal(self):
        if self.__scanner.current_char() not in config.quotes: return

        begin_quote = self.__scanner.current_char()

        while self.__scanner.next() != begin_quote:
            self.__word += self.__scanner.current_char()

        self.__new_token(Token_type.LITERAL)
        self.__reset_word()

    def __read_numeric_literal(self):
        if not self.__scanner.current_char().isnumeric(): return

        while self.__scanner.current_char().isnumeric():
            self.__word += self.__scanner.next()

        self.__new_token(Token_type.LITERAL)
        self.__reset_word()

    def __read_seperator(self):
        if self.__scanner.current_char() not in config.seperators: return

        self.__tokens.append(Token(self.__scanner.current_char(), Token_type.SEPERATOR))

    def tokenize(self):
        while not self.__scanner.is_at_end():
            self.__read_keyword()
            self.__read_operator()
            self.__read_string_literal()
            self.__read_numeric_literal()
            self.__read_seperator()

        return self.__tokens
