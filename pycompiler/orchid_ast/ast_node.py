from orchid_ast.ast_type import Ast_type

class Ast_node:
    def __init__(self, type=Ast_type.NONE):
        self.__type = type

    def type_is(self, check):
        return self.__type == check

    def get_type(self):
        return self.__type.name
    
    def set_type(self, type):
        self.__type = type
    
    def get_descendants(self):
        return []

    def __str__(self):
        return f"Ast_node of type {self.__type.name}"
