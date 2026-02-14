from util import util
from util.log_level import Log_level
from lexer.tokenizer import Tokenizer

class Module:
    def __init__(self, path):
        util.logger.log(f"Initializing new Module ({path})", Log_level.DEBUG)

        self.__path = path
        self.__str_content = "import \"stdlib\"\n\n"

        if util.path_to_name(path) == "stdlib": self.__str_content = ""

        self.__tokens = []
        self.__tokenizer = None

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

        self.__tokenizer = Tokenizer(self.__str_content)
        self.__tokens = self.__tokenizer.tokenize()

        util.logger.log(f"Read {len(self.__tokens)} tokens for Module ({self.__path})", Log_level.DEBUG)

