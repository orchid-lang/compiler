from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_type import Ast_type
from lexer.token_type import Token_type
from orchid_ast.ast_literal_node import Ast_literal_node
from orchid_ast.literal_type import Literal_type
from orchid_ast.ast_type import Ast_type
from util import util
from util.log_level import Log_level

class Ast_identifier_node(Ast_node):
    def __init__(self, scanner):
        super().__init__(Ast_type.NONE)
        self.__scanner = scanner
        self.__name = ""
        self.__args = []
        self.__parse()

    def __parse(self):
        util.logger.log(f"\tNow parsing: {self.__scanner.current_item()}", Log_level.VERBOSE)

        name = self.__scanner.next()

        if self.__scanner.preview().word_is("("):
            self.__scanner.next()
            args = []
            while not self.__scanner.next().word_is(")"):
                if self.__scanner.current_item().type_is(Token_type.LITERAL):
                    if self.__scanner.current_item().get_word().isnumeric():
                        args.append(Ast_literal_node(self.__scanner, Literal_type.NUMBER))
                    else:
                        args.append(Ast_literal_node(self.__scanner, Literal_type.STRING))
                else:
                    args.append(Ast_literal_node(self.__scanner, Literal_type.VARIABLE))
                
                if self.__scanner.preview().word_is(","):
                    self._scanner.next()

            self.set_type(Ast_type.CALL)
            self.__name = name
            self.__args = args

    def get_name(self):
        return self.__name
    
    def get_args(self):
        return self.__args
