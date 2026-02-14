import sys
import config
import util
from module import Module

def main():
    config.init()
    util.init()

    util.clean_target()

    module_path = util.get_module_path()
    module = Module(module_path)

if __name__ == "__main__":
    main()
