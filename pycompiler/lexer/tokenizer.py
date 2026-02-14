from util import util, config
from util.log_level import Log_level
from util.scanner import Scanner
from lexer.token import Token
from lexer.token_type import Token_type

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
        if not self.__scanner.current_item().isalpha(): return False

        self.__word += self.__scanner.current_item()
        while not self.__scanner.next().isspace() and self.__scanner.current_item() not in config.operators and self.__scanner.current_item() not in config.seperators:
            self.__word += self.__scanner.current_item()

        if self.__word not in config.keywords:
            self.__new_token(Token_type.IDENTIFIER)
            self.__reset_word()
            return True

        if self.__word == "then":
            self.__tokens += config.then_expands_to
        else:
            self.__new_token(Token_type.KEYWORD)

        self.__reset_word()
        return True

    def __read_operator(self):
        if self.__scanner.current_item() not in config.operators: return False

        self.__word += self.__scanner.current_item()
        while self.__scanner.current_item() in config.operators:
            self.__word += self.__scanner.next()

        self.__new_token(Token_type.OPERATOR)
        self.__reset_word()
        return True

    def __read_string_literal(self):
        if self.__scanner.current_item() not in config.quotes: return False

        begin_quote = self.__scanner.current_item()

        while self.__scanner.next() != begin_quote:
            self.__word += self.__scanner.current_item()

        self.__scanner.next()

        self.__new_token(Token_type.LITERAL)
        self.__reset_word()
        return True

    def __read_numeric_literal(self):
        if not self.__scanner.current_item().isnumeric(): return False

        while self.__scanner.current_item().isnumeric():
            self.__word += self.__scanner.next()

        self.__new_token(Token_type.LITERAL)
        self.__reset_word()
        return True

    def __read_seperator(self):
        if self.__scanner.current_item() not in config.seperators: return False

        self.__tokens.append(Token(self.__scanner.current_item(), Token_type.SEPERATOR))
        self.__scanner.next()
        return True

    def __read_whitespace(self):
        if not self.__scanner.current_item().isspace(): return False
        self.__scanner.next()
        return True

    def tokenize(self):
        while not self.__scanner.is_at_end():
            if self.__read_keyword(): pass
            elif self.__read_operator(): pass
            elif self.__read_string_literal(): pass
            elif self.__read_numeric_literal(): pass
            elif self.__read_seperator(): pass
            elif self.__read_whitespace(): pass

        return self.__tokens
