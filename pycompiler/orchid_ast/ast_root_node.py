from orchid_ast.ast_node import Ast_node
from orchid_ast.ast_type import Ast_type
from orchid_ast.ast_block import Ast_block
from util.scanner import Scanner
from util import util
from util.log_level import Log_level

class Ast_root_node(Ast_node):
    def __init__(self, tokens):
        super().__init__()
        self.__scanner = Scanner(tokens)
        self.__tree = []

    def generate(self):
        while not self.__scanner.is_at_end():
            token = self.__scanner.current_item()
            if token.word_is("start"):
                block = Ast_block(self.__scanner)
                block.parse()
                self.__tree.append(block.get_node())
            else:
                self.__scanner.next()

        for i, node in enumerate(self.__tree):
            util.logger.log(f"#{i}: {node}", Log_level.DEBUG)
