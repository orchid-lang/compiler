import subprocess
import sys

import config
from logger import Logger


def init():
    global logger

    logger = Logger()

def clean_target():
    subprocess.run("rm -r ./out".split(" "))
    subprocess.run("mkdir -p out".split(" "))

def get_module_path():
    module_path = config.default_module_path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    
    return module_path

def path_to_name(path):
    name = path.split("/")
    name = name[len(name) - 1]
    name = name.split("\\")
    name = name[len(name) - 1]
    name = name[:-4]
    return name
