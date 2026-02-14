from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_type import Ast_type
from lexer.token_type import Token_type
from util import util
from util.log_level import Log_level

class Ast_keyword_node(Ast_node):
    def __init__(self, scanner):
        super().__init__(Ast_type.NONE)
        self.__scanner = scanner
        self.__parse()
        
        self.condition = []
        self.id = None
        self.body = None

    # TODO: Somehow find a way to not have this function here following DRY principle.
    def __expect_token(self, to_expect):
        if not self.__scanner.current_item().word_is(to_expect):
            raise SyntaxError(f"Expected word '{to_expect}' got '{self.__scanner.current_item()}'!")
        self.__scanner.next()

    def __expect_type(self, to_expect):
        if not self.__scanner.current_item().type_is(to_expect):
            raise SyntaxError(f"Expected type '{to_expect}' got '{self.__scanner.current_item()}'!")
        
        x = self.__scanner.current_item()
        self.__scanner.next()
        return x

    def __parse(self):
        util.logger.log(f"\tNow parsing: {self.__scanner.current_item()}", Log_level.VERBOSE)

        if self.__scanner.current_item().word_is("if"):
            self.__expect_token("(")
            condition_tokens = []
            token = self.__scanner.next()
            while not token.word_is(")"):
                condition_tokens.append(token)
                token = next()
            self.__expect_token("then")
            # TODO: parse body
            self.__type = Ast_type.CONDITION
            self.condition = condition_tokens
        elif self.__scanner.current_item().word_is("let"):
            self.__scanner.next()
            name = self.__expect_type(Token_type.IDENTIFIER)
            self.__expect_token("=")
            util.logger.log(f"New variable: {name}", Log_level.DEBUG)
            
