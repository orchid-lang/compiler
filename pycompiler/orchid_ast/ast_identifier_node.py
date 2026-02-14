from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_type import Ast_type

class Ast_identifier_node(Ast_node):
    def __init__(self, scanner):
        super().__init__(Ast_type.NONE)
        self.__scanner = scanner
