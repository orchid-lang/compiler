from util import util
from lexer.token_type import Token_type
from util.log_level import Log_level
from orchid_ast.ast_identifier_node import Ast_identifier_node
from orchid_ast.ast_keyword_node import Ast_keyword_node

class Token:
    def __init__(self, word, type=Token_type.NONE):
        util.logger.log(f"Initializing new Token ('{word}', {type.name})", Log_level.DEBUG)
        self.__type = type
        self.__word = word

    def word_is(self, check):
        return self.__word == check
    
    def get_word(self):
        return self.__word
    
    def type_is(self, check):
        return self.__type == check
    
    def parse(self, scanner):
        if self.__type == Token_type.IDENTIFIER:
            return Ast_identifier_node(scanner)
        elif self.__type == Token_type.KEYWORD:
            return Ast_keyword_node(scanner)
        return False

    def __str__(self):
        return f"Token '{self.__word}' is a(n) {self.__type.name}"