import config
from log_level import Log_level
from datetime import datetime

class Logger:
    def __init__(self):
        self.__log_level = config.log_level

    def log(self, message, level=Log_level.INFO):
        if (level < self.__log_level):
            return
        
        print(f"[{datetime.now()}] [{level.name}] {message}")
