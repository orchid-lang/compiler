import util
from log_level import Log_level

class Module:
    def __init__(self, path):
        util.logger.log(f"Initializing new Module ({path})", Log_level.VERBOSE)

        self.__path = path
        self.__str_content = "import \"stdlib\"\n\n"

        if util.path_to_name(path) == "stdlib": self.__str_content = ""

    def read(self):
        util.logger.log(f"Reading Module ({self.__str_content})", Log_level.VERBOSE)

        f = open(self.__path)
        
        text = self.__str_content
        text += f.read()
        text = text.replace("\r", "")
        text = text.split("\n")
        text = " ".join(text)
        self.__str_content = text

        f.close()
    