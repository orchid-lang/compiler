from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_type import Ast_type

class Ast_literal_node(Ast_node):
    def __init__(self, scanner, type):
        super().__init__(Ast_type.VALUE)
        self.__scanner = scanner
        self.__type = type
