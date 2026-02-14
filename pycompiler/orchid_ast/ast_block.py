class Ast_block:
    def __init__(self, scanner):
        self.__scanner = scanner

    def parse(self):
        self.__scanner.next()

    def get_node(self):
        return "a"