from ast_type import Ast_type

class Ast_node:
    def __init__(self, type=Ast_type.NONE):
        self.__type__ = type