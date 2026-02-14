import util
import config
from log_level import Log_level
from token import Token
from token_type import Token_type

class Module:
    def __init__(self, path):
        util.logger.log(f"Initializing new Module ({path})", Log_level.DEBUG)

        self.__path = path
        self.__str_content = "import \"stdlib\"\n\n"

        if util.path_to_name(path) == "stdlib": self.__str_content = ""

        self.__tokens = []

    def read(self):
        util.logger.log(f"Reading Module ({self.__path})", Log_level.DEBUG)

        f = open(self.__path)
        
        text = self.__str_content
        text += f.read()
        text = text.replace("\r", "")
        text = text.split("\n")
        text = " ".join(text)
        self.__str_content = text

        f.close()
    
    def read_tokens(self):
        util.logger.log(f"Reading tokens for Module ({self.__path})", Log_level.DEBUG)
        
        current = 0
        text = self.__str_content
        word = ""
        while current < len(text):
            util.logger.log(f"\t- Current character: '{text[current]}'@{current}", Log_level.VERBOSE)

            if text[current].isalpha():
                while not text[current].isspace() and not text[current] in config.seperators:
                    word += text[current]
                    current += 1

                if word in config.keywords:
                    self.__tokens.append(Token(word, Token_type.KEYWORD))
                    if word == "then":
                        self.tokens += config.then_expands_to

                word = ""

            if text[current] in config.operators:
                while text[current] in config.operators:
                    word += text[current]
                    current += 1

                self.__tokens.append(Token(word, Token_type.OPERATOR))
                word = ""

            if text[current] == "\"" or text[current] == "'":
                original = text[current]
                current += 1
                while text[current] != original:
                    word += text[current]
                    current += 1

                self.__tokens.append(Token(word, Token_type.LITERAL))
                word = ""

            if text[current].isnumeric():
                while text[current].isnumeric():
                    word += text[current]
                    current += 1

                self.__tokens.append(Token(word, Token_type.LITERAL))
                word = ""

            if text[current] in config.seperators:
                self.__tokens.append(Token(word, Token_type.SEPERATOR))

            current += 1

        util.logger.log(f"Read {len(self.__tokens)} tokens for Module ({self.__path})", Log_level.DEBUG)

