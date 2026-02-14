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
operators = ["+", "-", "*", "/", "^", "=", "&", "|", "!"]
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
    # Part format: [('1', 'lit'), ('+', 'op'), ('1', 'lit')]
    # alt format: [('1', 'lit'), ('+', 'op'), ('1', 'lit'), ('*', 'op'), ('1', 'lit')]
    # Tree format: {"type": "op", "action": "add", left: ("1", "lit"), right: ("1", "lit")}
    # alt format: {"type": "op", "action": "multiply", left: {"type": "op", "action": "+", left: ("1", "lit"), right: ("1", "lit")}, right: ("1", "lit")}
    operations = {
        "+": "add",
        "-": "subtract",
        "*": "multiply",
        "/": "divide",
        "^": "power",
    }

    if not part:
        return None
    
    tree = part[0]

    i = 1
    while i < len(part):
        token, kind = part[i]
        right_token = part[i + 1]

        if kind != 'op':
            raise ValueError(f"Expected operator at position {i}, got {token}")
        
        tree = {
            "type": "op",
            "action": operations.get(token, token),
            "left": tree,
            "right": right_token
        }

        i += 2

    if (debugMode): print(f"generated tree: {tree}\n")

    return tree

def solve_tree(tree):
    if isinstance(tree, tuple):
        if tree[1] == 'lit':
            if str(tree[0]).isnumeric():
                return (float(tree[0]), "num")
            else:
                return (str(tree[0]), "str")
        else:
            return tree

    if isinstance(tree, dict) and tree["type"] == "op":
        left_val = solve_tree(tree["left"])
        right_val = solve_tree(tree["right"])

        if (
            isinstance(left_val, tuple) and left_val[1] in ("num", "str") and
            isinstance(right_val, tuple) and right_val[1] in ("num", "str")
        ):
            action = tree["action"]
            if action == "add":
                return (left_val[0] + right_val[0], left_val[1] if left_val[1] == right_val[1] else "mixed")
            elif action == "subtract":
                return (left_val[0] - right_val[0], left_val[1])
            elif action == "multiply":
                return (left_val[0] * right_val[0], left_val[1])
            elif action == "divide":
                return (left_val[0] / right_val[0], left_val[1])
            else:
                raise ValueError(f"Unknown operation: {action}")
        else:
            return {
                "type": "op",
                "action": tree["action"],
                "left": left_val,
                "right": right_val
            }

    raise ValueError(f"Invalid tree node: {tree}")

def evaluate_result(res, operations):
    if not operations:
        if str(res[0]).isnumeric():
            return float(res[0]) >= 1
        else:
            return res[0] == "true"
        
    results = []
    cur_op = 0
    i = 0
    while i < len(res):
        if cur_op < len(operations) and operations[cur_op][0] == "compare":
            _, comp_op = operations[cur_op]
            left = res[i]
            right = res[i + 1]

            if comp_op == "==":
                comp_res = left == right
            elif comp_op == "!=":
                comp_res = left != right
            elif comp_op == ">":
                comp_res = left > right
            elif comp_op == "<":
                comp_res = left < right
            elif comp_op == ">=":
                comp_res = left >= right
            elif comp_op == "<=":
                comp_res = left <= right
            else:
                raise ValueError(f"Unknown comparison: {comp_op}")
            
            results.append(bool(comp_res))
            i += 2
            cur_op += 1
        else:
            if str(res[0]).isnumeric():
                results.append(float(res[i]) >= 1)
            else:
                results.append(res[i] == "true")
            i += 1

    final_res = results[0]
    comb_i = 0
    for kind, value in operations:
        if kind == "combine":
            right_val = results[comb_i + i]
            if value == "&&":
                final_res = final_res and right_val
            elif value == "||":
                final_res = final_res or right_val
            else:
                raise ValueError(f"Unknown combiner: {value}")
            comb_i += 1
    
    return final_res

constant_condition_count = -1
non_constant_condition_count = -1
def parse_condition(_condition):
    global constant_condition_count, non_constant_condition_count
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
    else:
        non_constant_condition_count += 1
        for part in all_parts:
            new_parts.append(solve_tree(generate_tree(part)))
        if debugMode: print(f"Solved parts: {new_parts}\n")

        condition["condition"] = new_parts
        condition["id"] = non_constant_condition_count
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
                "id": None,
                "operations": [],
                "body": body,
            }
            return parse_condition(r)
        elif token == "let":
            next()
            name = expect_type("ident")
            expect("=")
            print(f"var name: {name}")
            var_value = []
            tok = next()
            while not (tok[1] == "kwd" and tok[0] == "end"):
                var_value.append(tok)
                tok = next()
            var_value = solve_tree(generate_tree(var_value))
            print(f"var value: {var_value}")
            return {
                "type": "definition",
                "value": var_value,
                "name": name,
            }
        

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

        if (debugMode): print(f"\tDefining function: {name}")

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
            return_type = expect_type("kwd")
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

var_section = [
    "section .data"
]

string_labels = []
str_count = 0

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
            if(debugMode): text_section.append(f"\t; statement: {statement}")
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
                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "
                        text_section.append(f"\tmov rdi, [{ext}{val}]")

                text_section.append(f"\tcall {name}")
                if len(args) > 0: text_section.append("\tpop rdi")
            elif statement["type"] == "condition":
                cond = statement["condition"][0] if isinstance(statement["condition"], list) and len(statement["condition"]) > 0 else statement["condition"]
                cond_label = f"start_condition_body_{statement['id']}"
                end_label = f"end_condition_body_{statement['id']}"
                text_section.append(f"{cond_label}:")

                if isinstance(cond, tuple):
                    val, kind = cond
                    if kind in ("var", "ident"):
                        is_param = False
                        for param in block['params']:
                            if param['name'] == val:
                                is_param = True

                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "

                        if is_param:
                            text_section.append("\tmov rax, rdi")
                        else:
                            text_section.append(f"\tmov rax, [{ext}{val}]")

                        text_section.append(f"\tcmp rax, 1")
                        text_section.append(f"\tjge {cond_label}_true")
                        
                        # TODO: allow 'true' string

                        text_section.append(f"\tjmp {end_label}")
                        text_section.append(f"{cond_label}_true:")
                    else:
                        text_section.append(f"\tjmp {end_label} ; unknown condition kind")
                elif isinstance(cond, dict):
                    # TODO: handle expression trees if needed
                    text_section.append(f"\tjmp {end_label} ; complex condition not implemented")
                else:
                    text_section.append(f"\tjmp {end_label} ; unknown condition type")

                for stmt in statement["body"]["body"]:
                    if stmt["type"] == "call":
                        name = stmt["name"]
                        args = stmt["args"]
                        if name not in functions and name != "callSharedLib":
                            pretext_section.append(f"extern {name}")
                        if len(args) > 0:
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
                                ext = ""
                                if platform.system() == "Darwin":
                                    ext = "rel "
                                text_section.append(f"\tmov rdi, [{ext}{val}]")
                        text_section.append(f"\tcall {name}")
                        if len(args) > 0:
                            text_section.append("\tpop rdi")

                text_section.append(f"\tjmp {end_label}")
                text_section.append(f"{end_label}:")
            elif statement["type"] == "definition":
                name = statement["name"]
                value = statement["value"]

                if isinstance(value, tuple):
                    val, kind = value
                    if kind == "num":
                        var_section.append(f"{name}: dq 0")
                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "
                        text_section.append(f"\tmov qword [{ext}{name}], {str(int(val))}")
                    elif kind == "str":
                        label = f"{name}_str"
                        string_labels.append((label, val))
                        var_section.append(f"{name}: dq {label}")
                    elif kind in ("var", "ident"):
                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "
                        text_section.append(f"\tmov rax, [{ext}{val}]")
                        text_section.append(f"\tmov qword [{ext}{name}], rax")

                    
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
        text_section.append(f"{block['name']}:")
        var_map = {}
        for i, arg in enumerate(block["params"]):
            if i < len(param_regs):
                var_map[arg["name"]] = param_regs[i]
            else:
                raise ValueError(f"Only {len(param_regs)} arguements(s) supported, tried to use {i + 1} in {module_name}")
            
        for statement in block["body"]:
            if(debugMode): text_section.append(f"\t; statement: {statement}")
            if(debugMode): print(f"\nstatement: {statement}")
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
                            text_section.append(f"\tlea rdi, [rel {label}]")
                        else:
                            text_section.append(f"\tmov rdi, {label}")
                    elif typ == "num":
                        text_section.append(f"\tmov rdi, {val}")
                    elif typ == "var":
                        # text_section.append(f"\tmov rdi, [{val}]")
                        pass
                    else:
                        raise Exception(f"[{module_name}] Unsupported argument type: {typ}")

                    text_section.append(f"\tcall {func}")

                    continue

                if len(args) > len(param_regs):
                    raise ValueError(f"Only {len(param_regs)} arguements(s) supported, tried to use {len(args)} for call {name} in {module_name}")

                for i, (val, typ) in enumerate(args):
                    if typ == "str":
                        label = f"str{str_count}"
                        str_count += 1
                        string_labels.append((label, val))
                        text_section.append(f"\tlea {param_regs[i]}, [rel {label}]")
                    elif typ == "num":
                        text_section.append(f"\tmov {param_regs[i]}, {val}")
                    elif typ == "var":
                        reg = var_map.get(val, "undef")
                        text_section.append(f"\tmov {param_regs[i]}, {reg}")

                if name == block["name"]:
                    text_section.append(f"\tjmp {name}")
                else:
                    text_section.append(f"\tcall {name}")
            elif statement["type"] == "condition":
                # Evaluate the condition at runtime: true if >=1 (number) or string 'true', or if variable, check at runtime
                cond = statement["condition"][0] if isinstance(statement["condition"], list) and len(statement["condition"]) > 0 else statement["condition"]
                cond_label = f"start_condition_body_{statement['id']}"
                end_label = f"end_condition_body_{statement['id']}"
                text_section.append(f"{cond_label}:")

                # Handle different condition types
                if isinstance(cond, tuple):
                    val, kind = cond
                    if kind in ("var", "ident"):
                        is_param = False
                        for param in block['params']:
                            if param['name'] == val:
                                is_param = True

                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "

                        if is_param:
                            text_section.append("\tmov rax, rdi")
                        else:
                            text_section.append(f"\tmov rax, [{ext}{val}]")

                        text_section.append(f"\tcmp rax, 1")
                        text_section.append(f"\tjge {cond_label}_true")
                        
                        # TODO: allow 'true' string

                        text_section.append(f"\tjmp {end_label}")
                        text_section.append(f"{cond_label}_true:")
                    else:
                        text_section.append(f"\tjmp {end_label} ; unknown condition kind")
                elif isinstance(cond, dict):
                    # TODO: handle expression trees if needed
                    text_section.append(f"\tjmp {end_label} ; complex condition not implemented")
                else:
                    text_section.append(f"\tjmp {end_label} ; unknown condition type")

                # Body of the condition
                for stmt in statement["body"]["body"]:
                    # Recursively emit code for statements in the condition body
                    # This is a simplified version; you may want to refactor for reuse
                    if stmt["type"] == "call":
                        name = stmt["name"]
                        args = stmt["args"]
                        if name not in functions and name != "callSharedLib":
                            pretext_section.append(f"extern {name}")
                        if len(args) > 0:
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
                                ext = ""
                                if platform.system() == "Darwin":
                                    ext = "rel "
                                text_section.append(f"\tmov rdi, [{ext}{val}]")
                        text_section.append(f"\tcall {name}")
                        if len(args) > 0:
                            text_section.append("\tpop rdi")
                    # Add more statement types as needed

                text_section.append(f"\tjmp {end_label}")
                text_section.append(f"{end_label}:")
            elif statement["type"] == "definition":
                name = statement["name"]
                value = statement["value"]

                if isinstance(value, tuple):
                    val, kind = value
                    if kind == "num":
                        var_section.append(f"{name}: dq 0")
                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "
                        text_section.append(f"\tmov qword [{ext}{name}], {str(int(val))}")
                    elif kind == "str":
                        label = f"{name}_str"
                        string_labels.append((label, val))
                        var_section.append(f"{name}: dq {label}")
                    elif kind in ("var", "ident"):
                        ext = ""
                        if platform.system() == "Darwin":
                            ext = "rel "
                        text_section.append(f"\tmov rax, [{ext}{val}]")
                        text_section.append(f"\tmov qword [{ext}{name}], rax")

            elif statement["type"] == "noop":
                # Do nothing.
                text_section.append(f"\t; Encountered noop block")

            else: raise ValueError(f"Unknown statement type ({statement["type"]}) in body")

        text_section.append("\tret")
        # text_section += body

    elif block["type"] == "import":
        # Already handled
        pass

    else: 
        raise ValueError(f"Unknown block type {block["type"]}!")
        
if len(string_labels) > 0:
    data_section.append("section .rodata")
for label, val in string_labels:
    data_section.append(f"{label}: db \"{val}\", 0")

full_program = pretext_section + var_section + text_section + data_section
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
