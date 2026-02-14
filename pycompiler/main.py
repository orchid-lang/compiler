import sys
import config
import util
from module import Module

def main():
    config.init()
    util.init()
    config.init_internal()

    util.clean_target()

    module_path = util.get_module_path()
    module = Module(module_path)
    module.read()
    module.read_tokens()

if __name__ == "__main__":
    main()
