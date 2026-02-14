from orchid_ast.ast_type import Ast_type

class Ast_node:
    def __init__(self, type=Ast_type.NONE):
        self.__type = type

    def get_type(self):
        return self.__type.name
