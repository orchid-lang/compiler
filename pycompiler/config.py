from log_level import Log_level
from token import Token
from token_type import Token_type

def init():
    global default_module_path, log_level

    default_module_path = "./compiler/main.orh"
    log_level = Log_level.VERBOSE

def init_internal():
    global keywords, seperators, operators, quotes, then_expands_to

    keywords = ["start", "function", "define", "as", "takes", "gives", "let", "make", "return", "end", "if", "then", "catch","_callSharedLib", "string", "int", "bool", "void", "nothing", "import"]
    seperators = ["{", "}", "(", ")", "[", "]", ","]
    operators = ["+", "-", "*", "/", "^", "=", "&", "|", "!"]
    quotes = ["\"", "'"]
    then_expands_to = [
        Token("start", Token_type.KEYWORD),
        Token("function", Token_type.KEYWORD),
        Token("_", Token_type.IDENTIFIER),
        Token("takes", Token_type.KEYWORD),
        Token("(", Token_type.SEPERATOR),
        Token(")", Token_type.SEPERATOR),
        Token("gives", Token_type.KEYWORD),
        Token("(", Token_type.SEPERATOR),
        Token(")", Token_type.SEPERATOR),
        Token("define", Token_type.KEYWORD),
        Token("as", Token_type.KEYWORD)
    ]
