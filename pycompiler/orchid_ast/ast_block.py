from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_main_node import Ast_main_node
from orchid_ast.ast_function_node import Ast_function_node
from orchid_ast.ast_function_arg import Ast_function_arg
from lexer.token import Token
from lexer.token_type import Token_type
from util import util
from util.log_level import Log_level

class Ast_block:
    def __init__(self, scanner):
        self.__scanner = scanner
        self.__node = Ast_node()

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
    
    def __define_function(self):
        self.__expect_token("function")
        name = self.__expect_type(Token_type.IDENTIFIER)
        util.logger.log(f"Defining function {name}", Log_level.DEBUG)
        self.__expect_token("takes")
        self.__expect_token("(")
        
        args = []
        while not self.__scanner.current_item().word_is(")"):
            arg = Ast_function_arg(self.__scanner)
            arg.parse()
            args.append(arg)
        
        self.__expect_token(")")
        self.__expect_token("gives")
        self.__expect_token("(")

        returns = []
        while not self.__scanner.current_item().word_is(")"):
            returns.append(self.__expect_type(Token_type.KEYWORD))

        self.__expect_token(")")

        return Ast_function_node(name, args, returns, None)

    def parse(self):
        self.__expect_token("start")
        token = self.__scanner.current_item()
        if token.word_is("main"):
            self.__node = Ast_main_node(None) # TODO: parse body content
            # self.__expect_token("end")
            return

        self.__node = self.__define_function()
        # self.__expect_token("end")

    def get_node(self):
        return self.__node
