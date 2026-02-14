from lexer.token_type import Token_type

class Ast_function_arg:
    def __init__(self, scanner):
        self.__type = ""
        self.__name = ""
        self.__scanner = scanner

    # TODO: Somehow find a way to not have this function here following DRY principle.
    def __expect_type(self, to_expect):
        if not self.__scanner.current_item().type_is(to_expect):
            raise SyntaxError(f"Expected type '{to_expect}' got '{self.__scanner.current_item()}'!")
        
        x = self.__scanner.current_item()
        self.__scanner.next()
        return x

    def parse(self):
        self.__type = self.__expect_type(Token_type.KEYWORD)
        self.__name = self.__expect_type(Token_type.IDENTIFIER)
    
    def get_name(self):
        return self.__name
    
    def get_type(self):
        return self.__type
        