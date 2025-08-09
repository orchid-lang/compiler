# Compile main.orh so that the compiler can be written in orchid to later compile itself
import sys
import subprocess
import platform
import os
module = "./compiler/main.orh"
if len(sys.argv) > 1:
    module = sys.argv[1]

debugMode = False
if os.path.exists("./.orchiddebug"):
    debugMode = True

is_main_module = True
if len(sys.argv) > 2:
    is_main_module = False

def path_to_name(path):
    name = path.split("/")
    name = name[len(name) - 1]
    name = name.split("\\")
    name = name[len(name) - 1]
    name = name[:-4]
    return name
 
module_name = path_to_name(module)
modules = [module_name]
if (debugMode): print(f"===== Working on {module_name} =====\n")

# clean target
subprocess.run("rm -r ./out".split(" "))
subprocess.run("mkdir -p out".split(" "))

# Get main.orh
main_f = open(module)
main_t = main_f.read()
if not module_name == "stdlib":
    main_t = f"import \"stdlib\"\n\n{main_t}"

main_l = main_t.replace("\r", "").split("\n")
main_j = ' '.join(main_l) + "\n"

# Read tokens

current = 0

tokens = []

keywords = ["start", "function", "define", "as", "takes", "gives", "let", "make", "return", "end", "if", "then", "catch","_callSharedLib", "string", "int", "bool", "void", "nothing", "import"]
seperators = ["{", "}", "(", ")", "[", "]"]
operators = ["+", "-", "*", "/", "^", "=", "&", "|"]
word = ""

while current < len(main_j):
    if main_j[current].isalpha():
        while not main_j[current].isspace() and not main_j[current] in seperators:
            word += main_j[current]
            current += 1
        
        if word in keywords:
            tokens.append((word, "kwd"))
            if word == "then":
                # Bunch of tokens to create a function so if can use the 'then {} end' format instead of the entire function definition.
                tokens += [('start', 'kwd'), ('function', 'kwd'), ('_', 'ident'), ('takes', 'kwd'), ('(', 'sep'), (')', 'sep'), ('gives', 'kwd'), ('(', 'sep'), (')', 'sep'), ('define', 'kwd'), ('as', 'kwd')]
        else:
            tokens.append((word, "ident"))

        word = ""

    if main_j[current] in operators:
        while main_j[current] in operators:
            word += main_j[current]
            current += 1

        tokens.append((word, "op"))
        word = ""

    if main_j[current] == "\"" or main_j[current] == "'":
        original = main_j[current]
        current += 1
        while main_j[current] != original:
            word += main_j[current]
            current += 1

        tokens.append((word, "lit"))
        word = ""

    if main_j[current].isnumeric():
        while main_j[current].isnumeric():
            word += main_j[current]
            current += 1

        tokens.append((word, "lit"))
        word = ""

    if main_j[current] == "(" or main_j[current] == ")" or main_j[current] == ",":
        tokens.append((main_j[current], "sep"))

    current += 1

if (debugMode): print(f"tokens: {tokens}\n")

# Convert into ast
current = 0

def preview_next():
    if current < len(tokens):
        return tokens[current]
    else:
        return (None, None)
    
def next():
    global current
    token = tokens[current]
    current += 1
    return token

def expect(value):
    token, _ = next()
    if not token == value:
        raise SyntaxError(f"Expected {value} got {token} in {module_name}")
    return token

def expect_type(value):
    token, kind = next()
    if not kind == value:
        raise SyntaxError(f"Expected type of {value} got {kind} ({token} in {module_name})")
    return token

def generate_tree(part):
    # TODO: generate tree
    return []

def solve_tree(tree):
    # TODO: 'solve' tree
    return tree

def evaluate_result(res, operations):
    # TODO: evaluate the result
    return True

constant_condition_count = -1
def parse_condition(_condition):
    global constant_condition_count
    condition = _condition
    c = condition["condition"]
    constant = True
    for token, kind in c:
        if not (kind == "lit" or kind == "op"):
            # If theres only literals and operators in the condition, it is constant.
            constant = False
            break
    
    current_part = []

    all_parts = []
    operations = []

    combiners = ["&&", "||"]
    comparers = ["==", ">", "<", "<=", ">=", "!="]

    for token in c:
        if token[1] == "op" and token[0] in combiners:
            all_parts.append(current_part)
            current_part = []
            operations.append(("combine", token[0]))
        elif token[1] == "op" and token[0] in comparers:
            all_parts.append(current_part)
            current_part = []
            operations.append(("compare", token[0]))
        else:
            current_part.append(token)

    if len(current_part) > 0:
        all_parts.append(current_part)

    if debugMode: print(f"all condition parts: {all_parts}\n")
    if debugMode: print(f"condition operations: {operations}\n")

    new_parts = []
    if constant:
        constant_condition_count += 1
        for part in all_parts:
            new_parts.append(solve_tree(generate_tree(part)))
        if debugMode: print(f"Solved parts: {new_parts}\n")

        print(condition)
        if evaluate_result(new_parts, operations):
            function_block = {
                "type": "function",
                "name": f"const_cond_{constant_condition_count}",
                "params": [],
                "returns": [],
                "body": condition["body"]["body"]
            }
            ast.append(function_block)
            return {
                "type": "call",
                "name": f"const_cond_{constant_condition_count}",
                "args": []
            }
        else:
            return {
                "type": "noop"
            }

    return condition

def parse():
    token, kind = preview_next()
    
    if kind == "ident":
        name, _ = next()
        if preview_next()[0] == "(":
            next()
            args = []
            while True:
                arg_token, arg_kind = preview_next()
                if arg_token == ")":
                    next()
                    break
                arg_val, arg_type = next()
                if arg_type == "lit":
                    if arg_val.isnumeric():
                        args.append((arg_val, "num"))
                    else:
                        args.append((arg_val, "str"))
                else:
                    args.append((arg_val, "var"))

                if preview_next()[0] == ",":
                    next()
            return {
                "type": "call",
                "name": name,
                "args": args
            }
        else:
            return {
                "type": "dunno",
                "value": name
            }
    elif kind == "kwd":
        if token == "if":
            next()
            expect("(")
            condition_tokens = []
            token = next()
            while not token[0] == ")":
                condition_tokens.append(token)
                token = next()
            expect("then")
            body = parse_block()
            r = {
                "type": "condition",
                "condition": condition_tokens,
                "body": body,
            }
            return parse_condition(r)


def parse_define():
    expect("define")
    expect("as")
    body = []
    while True:
        token, _ = preview_next()
        if token == "end":
            break
        body.append(parse())
    return body

def parse_import():
    expect("import")
    path = expect_type("lit")
    if path == "stdlib":
        # TODO: get path to stdlib
        path = "./compiler/stdlib.orh"
    elif not str(path).__contains__("/"):
        rel = module[:-(len(module_name) + 4)]
        path = f"{rel}{path}"

    if not path.endswith(".orh"):
        path = f"{path}.orh"

    name = path_to_name(path)
    modules.append(name)

    subprocess.run(["python3", sys.argv[0], path, "not_main_module_flag"])

    return {
        "type": "import",
        "origin": path,
        "name": name
    }

def parse_block():
    expect("start")
    token, _ = next()
    if token == 'main':
        block = {
            "type": "main",
            "body": parse_define()
        }
        expect("end")
        return block
    else:
        if not token == "function":
            raise SyntaxError(f"Expected function got '{token}' in {module_name}")
        
        name = expect_type("ident")
        expect("takes")
        expect("(")
        
        args = []
        while not preview_next()[0] == ")":
            arg_type = expect_type("kwd")
            arg_name = expect_type("ident")
            args.append({
                "name": arg_name,
                "type": arg_type,
            })

        expect(")")
        expect("gives")
        expect("(")
        
        returns = []
        while not preview_next()[0] == ")":
            return_type = expect_type("ident")
            returns.append(return_type)

        expect(")")

        block = {
            "type": "function",
            "name": name,
            "params": args,
            "returns": returns,
            "body": parse_define()
        }
        expect("end")
        return block

ast = []
while current < len(tokens):
    token, _ = preview_next()
    if token == "start":
        ast.append(parse_block())
    elif token == "import":
        ast.append(parse_import())
    else:
        next()

if (debugMode): print(f"ast: {ast}")

# Generate assembly
outfile = open(f"./out/{module_name}.asm", "w+")
lines = []
data_section = []
pretext_section = []
text_section = [
    "section .text",
]

string_labels = []
str_count = 0

conditionals_count = 0

functions = {}

for block in ast:
    if(debugMode): print(f"\nblock: {block}")

    if(debugMode): text_section.append(f"; {block}")

    if block["type"] == "main":
        if platform.system() == "Darwin":
            pretext_section.append("global _main")
            text_section.append("_main:")
        else:
            pretext_section.append("global main")
            text_section.append("main:")
        for statement in block["body"]:
            if(debugMode): print(f"\nstatement: {statement}")
            if statement["type"] == "call":
                name = statement["name"]
                args = statement["args"]

                if name not in functions and name != "callSharedLib":
                    pretext_section.append(f"extern {name}")

                if len(args) > 0:
                    # TODO: multiple args
                    text_section.append("\tpush rdi")
                    (val, typ) = args[0]
                    if typ == "str":
                        label = f"str{str_count}"
                        str_count += 1
                        string_labels.append((label, val))
                        if platform.system() == "Darwin":
                            text_section.append(f"\tlea rdi, [rel {label}]")
                        else:
                            text_section.append(f"\tmov rdi, {label}")
                    elif typ == "num":
                        text_section.append(f"\tmov rdi, {val}")
                    elif typ == "var":
                        text_section.append(f"\tmov rdi, [{val}]")

                text_section.append(f"\tcall {name}")
                if len(args) > 0: text_section.append("\tpop rdi")
            elif statement["type"] == "condition":
                text_section.append(f"start_condition_body_{conditionals_count}:")
                # TODO implement condition
                text_section.append(f"\tjmp end_condition_body_{conditionals_count}")
                text_section.append(f"end_condition_body_{conditionals_count}:")
                conditionals_count += 1
            elif statement["type"] == "noop":
                # Do nothing.
                text_section.append(f"\t; Encountered noop block")

            else: raise ValueError(f"Unknown statement type ({statement["type"]}) in body")
        text_section.append("\tret")

    elif block["type"] == "function":
        pretext_section.append(f"global {str(block["name"])}")
        functions[block["name"]] = block
        # Just rdi for now as mentioned before, just one arg supported for now
        param_regs = ["rdi"]
        body = [f"{block['name']}:"]
        var_map = {}
        for i, arg in enumerate(block["params"]):
            if i < len(param_regs):
                var_map[arg["name"]] = param_regs[i]
            else:
                raise ValueError(f"Only {len(param_regs)} arguements(s) supported, tried to use {i + 1} in {module_name}")
            
        for statement in block["body"]:
            if statement["type"] == "call":
                name = statement["name"]
                args = statement["args"]

                if name not in functions and name != "callSharedLib":
                    pretext_section.append(f"extern {name}")

                if name == "callSharedLib":
                    lib = args[0][0]
                    func = args[1][0]
                    arg = args[2]

                    pretext_section.append(f"extern {func}")
                    val, typ = arg
                    if typ == "str":
                        label = f"str{str_count}"
                        str_count += 1
                        string_labels.append((label,', '.join([str(ord(c)) for c in val])))
                        if platform.system() == "Darwin":
                            body.append(f"\tlea rdi, [rel {label}]")
                        else:
                            body.append(f"\tmov rdi, {label}")
                    elif typ == "num":
                        body.append(f"\tmov rdi, {val}")
                    elif typ == "var":
                        # text_section.append(f"\tmov rdi, [{val}]")
                        pass
                    else:
                        raise Exception(f"[{module_name}] Unsupported argument type: {typ}")

                    body.append(f"\tcall {func}")

                    continue

                if len(args) > len(param_regs):
                    raise ValueError(f"Only {len(param_regs)} arguements(s) supported, tried to use {len(args)} for call {name} in {module_name}")

                for i, (val, typ) in enumerate(args):
                    if typ == "str":
                        label = f"str{str_count}"
                        str_count += 1
                        string_labels.append((label, val))
                        body.append(f"\tlea {param_regs[i]}, [rel {label}]")
                    elif typ == "num":
                        body.append(f"\tmov {param_regs[i]}, {val}")
                    elif typ == "var":
                        reg = var_map.get(val, "undef")
                        body.append(f"\tmov {param_regs[i]}, {reg}")

                if name == block["name"]:
                    body.append(f"\tjmp {name}")
                else:
                    body.append(f"\tcall {name}")

        body.append("\tret")
        text_section += body

    elif block["type"] == "import":
        # Already handled
        pass

    else: 
        raise ValueError(f"Unknown block type {block["type"]}!")
        
if len(string_labels) > 0:
    data_section.append("section .rodata")
for label, val in string_labels:
    data_section.append(f"{label}: db \"{val}\", 0")

full_program = pretext_section + text_section + data_section
outfile.write("\n".join(full_program) + "\n")
outfile.close()

if (debugMode): print(f"===== Finished {module_name} =====\n")

if (is_main_module):
    type = "elf64"
    if platform.system() == "Darwin":
        type = "macho64"
    elif platform.system() == "Windows":
        type = "win64"
    else:
        raise NotImplementedError("Unsupported system!")
    
    for module_ in modules:
        assamble_cmd = f"nasm -f {type} ./out/{module_}.asm -o ./out/{module_}.o"
        subprocess.run(assamble_cmd.split(" "))
    
    if "stdlib" in modules:
        platform_target = ""
        if platform.system() == "Darwin":
            platform_target = "-arch x86_64 "
        stdlib_build_cmd = f"gcc {platform_target} -c ./compiler/orchidlibstd.c -o ./out/orchidlibstd.o"
        subprocess.run(stdlib_build_cmd.split(" "))
    
    modules.append("orchidlibstd")

    link_cmd = "gcc "
    if platform.system() == "Darwin":
        link_cmd += "-arch x86_64 "
    for module_ in modules:
        link_cmd += f"./out/{module_}.o "
    link_cmd += "-o ./out/program"
    subprocess.run(link_cmd.split(" "))
    if not platform.system == "Windows":
        subprocess.run("chmod +x ./out/program".split(" "))
