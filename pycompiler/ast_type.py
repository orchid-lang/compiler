from enum import Enum

class Ast_type(Enum):
    IMPORT = 0,
    MAIN = 1,
    FUNCTION = 2
    CALL = 3
    CONDITION = 4,
    DEFINITION = 5,
    OPERATION = 6,
    VALUE = 7
    NONE = -1
