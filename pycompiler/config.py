from log_level import Log_level

def init():
    global default_module_path, log_level

    default_module_path = "./compiler/main.orh"
    log_level = Log_level.VERBOSE
