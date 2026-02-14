from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_main_node import Ast_main_node
from lexer.token import Token
from lexer.token_type import Token_type

class Ast_block:
    def __init__(self, scanner):
        self.__scanner = scanner
        self.__node = Ast_node()

    def __expect_token(self, to_expect):
        if not self.__scanner.current_item().word_is(to_expect):
            raise SyntaxError(f"Expected '{to_expect}' got '{self.__scanner.current_item()}'!")
        self.__scanner.next()

    def parse(self):
        self.__expect_token("start")
        token = self.__scanner.current_item()
        if token.word_is("main"):
            self.__node = Ast_main_node(None) # TODO: parse body content
            # self.__expect_token("end")
            return
        
        if not token.word_is("function"):
            raise SyntaxError(f"Expected function got '{token}'!")
    
        # self.__expect_token("end")

    def get_node(self):
        return self.__node