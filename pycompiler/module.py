import util

class Module:
    def __init__(self, path):
        self.__path = path
        self.__str_content = ""
        util.logger.log(f"Initializing new Module ({path})")

    def read(self):
        pass