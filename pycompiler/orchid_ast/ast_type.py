from enum import Enum

class Ast_type(Enum):
    IMPORT = 0
    FUNCTION = 1
    CALL = 2
    CONDITION = 3
    DEFINITION = 4
    OPERATION = 5
    VALUE = 6
    NONE = -1
