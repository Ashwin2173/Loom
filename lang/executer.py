import os
import orjson
import importlib

from utils.error import PythonError, CustomError
from utils.props import Props
from lang.variable import Variable
from lang.expression import Execute

class BlockExecutor:
    def __init__(self, block_name:str, block_token:list, variable_pool:Variable, args:list) -> None:
        self.block_name = block_name
        self.block_token = block_token
        self.args = args
        self.body = None
        self.body = block_token.get(Props.h_code.get("body"))
        self.variable_pool = variable_pool
        self.pointer = -1
        self.return_value = None

        self.__init_args()
        self.pyargs = list()

    def get_ret(self):
        return self.return_value

    def get_variable_pool(self):
        return self.variable_pool
    
    def __init_args(self):
        if(self.block_name[0] != "."): # this is a function block
            arguments = self.block_token.get(Props.h_code.get("args"))
            assert len(self.args) == len(arguments), f"'{self.block_name}' required {len(arguments)} arguments, but given {len(self.args)}"

            for item in range(len(arguments)):
                name = arguments[item]
                value = self.args[item]
                self.variable_pool.create(name)
                self.variable_pool.set(name, value)

    def __expression(self, token:dict) -> any:
        expression = token.get(Props.h_code.get("exp"))
        value = Execute(tokens=expression,
                        variable_pool=self.variable_pool).run()
        return value
    
    def peek(self) -> dict:
        return self.body[self.pointer]
    
    def step(self) -> None:
        self.pointer += 1

    def step_back(self) -> None:
        self.pointer -= 1

    def execute(self) -> None:
        if(self.pointer >= len(self.body)):
            return 2
        token = self.body[self.pointer]
        method = token.get(Props.h_code.get("method"))
        if(method == Props.h_code.get("var")):
            name = token.get(Props.h_code.get("name"))
            self.variable_pool.create(name)

        elif(method == Props.h_code.get("assign")):
            name = token.get(Props.h_code.get("name"))
            value = self.__expression(token)
            self.variable_pool.set(name, value)
        
        elif(method == Props.h_code.get("if")):
            value = self.__expression(token)
            if(value):
                goto = token.get(Props.h_code.get("goto"))
                # Orchestrator.block_in(goto)
                return 3, goto
            elif(self.pointer + 1 < len(self.body)): # else block
                token = self.body[self.pointer + 1]
                method = token.get(Props.h_code.get("method"))

                if(method == Props.h_code.get("else")):
                    goto = token.get(Props.h_code.get("goto"))
                    # Orchestrator.block_in(block_name=goto)
                    return 3, goto
                    
        elif(method == Props.h_code.get("else")):
            pass

        elif(method == Props.h_code.get("while")):
            value = self.__expression(token)
            goto = token.get(Props.h_code.get("goto"))
            if(value):
                return 3, goto

        elif(method == Props.h_code.get("pyimport")):
            name = token.get(Props.h_code.get("name"))
            try:
                importlib.import_module(name)
            except:
                raise PythonError("failed to pyimport")

        elif(method == Props.h_code.get("pycall")):
            m_name = token.get(Props.h_code.get("m_name"))
            name = token.get(Props.h_code.get("name"))
            mod = importlib.import_module(m_name)
            fn = getattr(mod, name)
            try:
                Orchestrator.set_reg(fn(self.pyargs))
            except Exception as err:
                raise PythonError(err)
            reg = Orchestrator.get_reg()
            if(reg != None and type(reg) not in {str, list, int, float}):
                raise PythonError(f"invalid return from python (type: {type(reg)})")
            self.pyargs = list()

        elif(method == Props.h_code.get("raise")):
            error_name = token.get(Props.h_code.get("name"))[2].get("raw")
            error_message = self.__expression(token)
            raise CustomError(error_name, error_message)

        elif(method == Props.h_code.get("pyarg")):
            value = self.__expression(token)
            self.pyargs.append(value)

        elif(method == Props.h_code.get("ret")):
            value = self.__expression(token)
            self.return_value = value
            return 1
        
        elif(method == Props.h_code.get("fn_call")):
            self.__expression(token)

        else:
            print(token)
            assert False, "invalid or unimplemented method"
        return 0

class Orchestrator:
    program = None
    imports = None
    blocks = None
    stack = list() # name, block_exec

    def init(program:any) -> None:
        Orchestrator.imports = program.get(Props.h_code.get("import"))
        Orchestrator.blocks = program.get(Props.h_code.get("blocks"))
        Orchestrator.imported_modules = set()
 
        Orchestrator.program = program
        Orchestrator.init_imports(Orchestrator.imports)
        Orchestrator.block_in("main", [Props.p_args])

    def get_reg() -> any:
        return Orchestrator.program.get(Props.h_code.get("reg"))

    def set_reg(value:any) -> None:
        Orchestrator.program[Props.h_code.get("reg")] = value

    def get_ret(block_name:str) -> any:
        return Orchestrator.blocks.get(block_name).get(Props.h_code.get("ret"))
    
    def set_ret(block_name:str, value:any) -> None:
        Orchestrator.blocks.get(block_name)[Props.h_code.get("ret")] = value

    def get_block_name() -> str:
        assert len(Orchestrator.stack) >= 1, f"empty block stack"
        return Orchestrator.stack[-1][0]

    def init_imports(import_list:list) -> None:
        for module in import_list:
            if(module not in Orchestrator.imported_modules):
                Orchestrator.imported_modules.add(module)
                
                module_path = os.path.join(Props.mod_path, module + ".mod")
                raw_module = None
                try:
                    module_file = open(module_path)
                    raw_module = orjson.loads(module_file.read())
                except FileNotFoundError: 
                    raise ModuleNotFoundError(f"'{module}' doesn't exist in 'loom_libs'")
                assert raw_module != None, "internal error during importing of '{module}'"

                sub_modules = raw_module.get(Props.h_code.get("import"))
                Orchestrator.init_imports(sub_modules)

                m_blocks = raw_module.get(Props.h_code.get("blocks"))
                for m_block_name, m_block_body in m_blocks.items():
                    if(m_block_name[0] == "."):
                        Orchestrator.blocks[m_block_name] = m_block_body
                    else:
                        Orchestrator.blocks[module + "." + m_block_name] = m_block_body

                Orchestrator.block_in(module + ".init", [])

    def block_in(block_name:str, args:list=list()) -> None:
        assert block_name in Orchestrator.blocks, f"undefined function block '{block_name}'"
        assert len(Orchestrator.stack) <= 200, f"block stack overflow"
        sub_stack = [] # name, block_exec

        variable_pool =  Variable(block_name)

        block_action = Orchestrator.blocks.get(block_name)
        block_exec = BlockExecutor(
            block_name = block_name,
            block_token = block_action,
            variable_pool = variable_pool,
            args = args
        )

        info = (block_name, block_exec)
        sub_stack.append(info)
        Orchestrator.stack.append(info)

        while len(sub_stack) != 0:
            block_exec = sub_stack[-1][1]
            block_exec.step()
            ret_value = block_exec.execute()
            if(ret_value == 1):
                for _ in range(len(sub_stack)):
                    Orchestrator.block_out()
                t_ret = sub_stack[-1][1].get_ret()
                return t_ret
            elif(ret_value == 2):
                assert len(sub_stack) >= 1, f"sub block stack underflow"
                sub_stack.pop()
                Orchestrator.block_out()
            elif(type(ret_value) == tuple):
                variable_pool = sub_stack[0][1].get_variable_pool()
                if(ret_value[0] == 3):
                    sub_block_name = ret_value[1]
                    sub_block_action = Orchestrator.blocks.get(sub_block_name)
                    sub_block_exec = BlockExecutor(
                        block_name = sub_block_name,
                        block_token = sub_block_action,
                        variable_pool = variable_pool,
                        args = list()
                    )

                    info = (sub_block_name, sub_block_exec)
                    sub_stack.append(info)
                    Orchestrator.stack.append(info)
                    if(sub_block_name[:len(".wh")] == ".wh"):
                        block_exec.step_back()


    def block_out() -> None:
        assert len(Orchestrator.stack) >= 1, f"block stack underflow"
        Orchestrator.stack.pop()