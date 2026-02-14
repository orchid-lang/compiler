from util import util
from log_level import Log_level

class Scanner:
    def __init__(self, content):
        self.__current = 0
        self.__content = content

    def current_char(self):
        return self.__content[self.__current]

    def next(self):
        self.__current += 1
        return self.current_char()
    
    def is_at_end(self):
        util.logger.log(f"\tScanner at: {self.__current + 1} / {len(self.__content)}", Log_level.VERBOSE)
        return self.__current  >= len(self.__content) - 1
    
    def __str__(self):
        return f"Scanner at #{self.__current}/{len(self.__content)}"
        