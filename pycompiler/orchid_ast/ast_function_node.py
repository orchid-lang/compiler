from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_type import Ast_type

class Ast_function_node(Ast_node):
    def __init__(self, name, params, returns, body):
        super().__init__(Ast_type.FUNCTION)
        self.__name = name
        self.__params = params
        self.__returns = returns
        self.__body = body

    def __str__(self):
        return f"Ast_function_node: {self.__name.get_word()}"