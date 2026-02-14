import sys
import config
import util
from module import Module

def main():
    config.init()
    util.init()

    module_path = config.default_module_path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    module = Module(module_path)

if __name__ == "__main__":
    main()
