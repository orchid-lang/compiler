from orchid_ast.ast_function_node import Ast_function_node
from orchid_ast.ast_type import Ast_type

class Ast_main_node(Ast_function_node):
    def __init__(self, body):
        super().__init__("main", [], [], body)
