from enum import Enum

class Token_type(Enum):
    KEYWORD = 0
    IDENTIFIER = 1
    OPERATOR = 2
    LITERAL = 3
    SEPERATOR = 4
    NONE = -1
