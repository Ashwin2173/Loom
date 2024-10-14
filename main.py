import os
import sys
import time
import orjson

from utils.walk import Walk
from utils.props import Props
from utils.console import info, error

from lang.hill import Hill
from lang.lexer import lexify
from lang.executer import Orchestrator
from utils.error import VariableError, ExpressionError, PythonError, CustomError

def main(args):
    LOOM_EXT = ".loom"
    HILL_EXT = ".hill"
    MOD_EXT = ".mod"
    start_time = time.time()

    Props.mod_path = os.getenv("loom_libs", None)
    if(Props.mod_path == None):
        error("Error: no config of 'loom_libs' found")
        exit(1)
    if(len(args) < 1 or args[0][-len(LOOM_EXT):] != LOOM_EXT):
        info("USAGE: loom <std_file> [options]")
        info("<std_file>: *.loom file")
        info("options:")
        info("    --module: generate the *.module file")
        info("    --time: stdout time taken to run the program")
        info("    --hill: dump the init state of the file")
        info("    --execute: execute the program")
        exit(1)

    init_file(args[0])      # initialize raw_program
    Props.p_args = args

    tokens = None
    try:
        tokens = lexify()
        if("--tokens" in args):
            for token in tokens:
                print(token)
    except AssertionError as err:
        error(f"At {args[0]} \nSyntaxError: {err}")
        exit(1)
    except Exception as err:
        except_message("Lexify", err)

    init_state = hill(tokens, args[0])
    if("--hill" in args):
        hill_file_path = args[0][:-len(LOOM_EXT)] + HILL_EXT
        with open(hill_file_path, 'wb') as f:
            f.write(
                orjson.dumps(init_state, option=orjson.OPT_NON_STR_KEYS)
            )
        info(f"Info: created '{hill_file_path}' file.")

    if("--module" in args):
        hill_file_path = args[0][:-len(LOOM_EXT)] + MOD_EXT
        with open(hill_file_path, 'wb') as f:
            f.write(
                orjson.dumps(init_state, option=orjson.OPT_NON_STR_KEYS)
            )
        info(f"Info: created '{hill_file_path}' file.")

    if("--execute" in args):
        execute(init_state, args[0])
    
    if("--time" in args):
        time_taken = round(time.time() - start_time, 2)
        info(f"Info: Program took approx. {time_taken}s")

def init_file(file_path:str) -> None:
    try:
        program = open(file_path, 'r')
        Props.file_path = file_path
        Props.raw_program = program.read()
        program.close()
    except FileNotFoundError:
        error(f"Error: '{file_path}' does not exist")
        exit(1)
    except Exception as err_message:
        except_message(context="file init", message=err_message)

def except_message(context:str, message:str, doquit:bool=True) -> None:
    error("Error code 5: ")
    error(f"during '{context}'")
    error(message)
    if(doquit):
        exit(1)

def hill(tokens:list, path:str) -> dict:
    hill = None
    walk = Walk(tokens)

    # hill_obj = Hill(walk)
    # hill = hill_obj.hillify()
    try:
        hill_obj = Hill(walk)
        hill = hill_obj.hillify()
    except AssertionError as err:
        hill_error_trace(walk, err, path)
    except ExpressionError as err:
        hill_error_trace(walk, err, path)
    except IndexError:
        hill_error_trace(walk, "walkfault", path)
    except Exception as err:
        except_message("Hill", err)
    return hill

def execute(hill:dict, path:str) -> None:
    # Orchestrator.init(hill)
    try:
        Orchestrator.init(hill)
        pass
    except AssertionError as err: 
        print_stack_trace("ExecutionError", err, path)
    except KeyboardInterrupt:
        print_stack_trace("InterruptError", "forced interrupt", path)
    except ExpressionError as err:
        print_stack_trace("ExpressionError" ,f"Bad Expression [processed_expression: {err.expression}]", path)
    except VariableError as err:
        print_stack_trace("VariableError", err, path)
    except ModuleNotFoundError as err:
        print_stack_trace("ImportError", err, path)
    except CustomError as err:
        error_name = err.error_name
        error_message = str(err)
        print_stack_trace(error_name, error_message, path)
    except PythonError as err:
        print_stack_trace("PythonError", err, path)
    except Exception as err:
        block_exec = Orchestrator.stack[-1][1]
        line = block_exec.body[block_exec.pointer].get(Props.h_code.get("line"))
        path = (" > ".join([item[0] for item in Orchestrator.stack]))
        except_message("Orchestrator", f"At line {line},\nstack: {path} \nInternal Error: {err}")

def print_stack_trace(title, err, path):
    stack_trace = Orchestrator.stack
    error("Error Stack Trace: ")
    error(f"During File '{path}'")
    for trace in stack_trace:
        line = trace[1].peek().get(Props.h_code.get("line"))
        error(f"    In {trace[0]}, line {line}")
    try:
        raw_line = Props.raw_program.split('\n')[line - 1].lstrip()
        error(f"> {raw_line}")
    except:
        pass
    error(f"{title}: {err}")
    exit(1)

def hill_error_trace(walk, err, path):
    line = walk.peek()[1]
    error(f"During hill on file '{path}', line {line}")
    try:
        raw_line = Props.raw_program.split("\n")[line - 1].lstrip()
        error(f"    > {raw_line}")
    except:
        pass
    error(f"SyntaxError: {err}")
    exit(1)

if(__name__ == "__main__"):
    # main([".\\examples\\test.loom", "--tokens"])
    main(sys.argv[1:])