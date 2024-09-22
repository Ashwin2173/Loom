import uuid

from lang.expression import Build

from utils.walk import Walk
from utils.props import Props

class Hill:
    def __init__(self, tokens:Walk):
        self.tokens = tokens
        self.imports = set()
        self.blocks = dict()
        self.stack = []

    def hillify(self):
        while self.tokens.next():
            token = self.tokens.peek()
            if(token[0] == Props.t_keywords.get("import")):
                # assert len(self.stack) == 0, "'import' statement inside function definition"
                self.__check_scope(usage="import", local=False)
                self.tokens.next()
                module = self.tokens.peek()
                assert module[0] == Props.t_indentifier, "expected 'indentifer' for keyword 'import'"

                self.imports.add(module[2].get("raw"))
                
                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
            
            elif(token[0] == Props.t_keywords.get("fn")):
                # assert len(self.stack) == 0, "function nesting is not allowed"
                self.__check_scope(usage="fn", local=False, message="function nesting is not allowed")

                self.tokens.next()
                fn = self.tokens.peek()
                fn_name = fn[2].get("raw")
                assert fn[0] == Props.t_indentifier, "expected 'indentifer' for keyword 'fn'"
                assert fn_name not in self.blocks, f"re-declaration of function '{fn_name}'"
                
                sep = False
                if(self.tokens.peek(offset=1)[0] == Props.t_symbols.get(":")):
                    self.tokens.next()
                    sep = True

                fn_args = list()
                while self.tokens.peek(offset=1)[0] != Props.t_symbols.get("{"):
                    self.tokens.next()
                    arg = self.tokens.peek()
                    assert arg[0] == Props.t_indentifier, "expected 'indentifer'"
                    arg_name = arg[2].get("raw")
                    assert arg_name not in fn_args, f"redundant arg '{arg_name}' in function definition"
                    fn_args.append(arg_name)
                    
                if(len(fn_args) != 0):
                    assert sep, "expected ':'"
                
                block_info = {
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("args"): fn_args,
                    Props.h_code.get("body"): list(),
                    Props.h_code.get("ret"): None
                }
                self.blocks[fn_name] = block_info
                self.stack.append(fn_name)
                self.tokens.next()

            elif(token[0] == Props.t_keywords.get("ret")):
                # assert len(self.stack) != 0, "usage of 'ret' in global scope"
                self.__check_scope(usage="ret")

                self.tokens.next()
                expression_tokens = self.tokens.until()
                expression = Build(expression_tokens).build() # todo: fix this
                return_info = {
                    Props.h_code.get("method"): Props.h_code.get("ret"),
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("exp"): expression
                }
                assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                self.__add_local(return_info)

            elif(token[0] == Props.t_keywords.get("raise")):
                self.__check_scope(usage="raise")

                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_indentifier, "expected an indentifier"
                exception_name = self.tokens.peek()

                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get(","), "expected ','"

                self.tokens.next()
                expression_tokens = self.tokens.until()
                expression = Build(expression_tokens).build()
                raise_info = {
                    Props.h_code.get("method"): Props.h_code.get("raise"),
                    Props.h_code.get("name"): exception_name,
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("exp"): expression
                }
                assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                self.__add_local(raise_info)
                
            
            elif(token[0] == Props.t_keywords.get("var")):
                # assert len(self.stack) != 0, "usage of 'ret' in global scope"
                self.__check_scope(usage="var")
                
                self.tokens.next()
                var = self.tokens.peek()
                assert var[0] == Props.t_indentifier, "expected 'identifier'"
                var_name = var[2].get("raw")

                if(self.tokens.peek(offset=1)[0] != Props.t_symbols.get("=")):
                    self.tokens.next()
                    assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                else:
                    self.tokens.prev()
                
                var_info = {
                    Props.h_code.get("method"): Props.h_code.get("var"),
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("name"): var_name
                }
                self.__add_local(var_info)

            elif(token[0] == Props.t_keywords.get("if")):
                self.__check_scope(usage="if")

                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get("("), "expected '('"

                self.tokens.next()
                # expression_tokens = self.tokens.until(target=[Props.t_symbols.get("{")])
                expression_tokens = self.tokens.until(stack=True)
                expression = Build(expression_tokens).build() # todo: fix this

                assert self.tokens.peek()[0] == Props.t_symbols.get("{"), "expected '{'"

                bl_name = ".if" + str(uuid.uuid4().hex)

                if_jump_info = {
                    Props.h_code.get("method"): Props.h_code.get("if"),
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("exp"): expression,
                    Props.h_code.get("goto"): bl_name
                }
                self.__add_local(if_jump_info)

                if_info = {
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("body"): list(),
                }
                self.blocks[bl_name] = if_info
                self.stack.append(bl_name)

            elif(token[0] == Props.t_keywords.get("while")):
                self.__check_scope(usage="while")

                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get("("), "expected '('"

                self.tokens.next()
                # expression_tokens = self.tokens.until(target=[Props.t_symbols.get("{")])
                expression_tokens = self.tokens.until(stack=True)
                expression = Build(expression_tokens).build() # todo: fix this

                assert self.tokens.peek()[0] == Props.t_symbols.get("{"), "expected '{'"

                bl_name = ".while" + str(uuid.uuid4().hex)

                while_jump_info = {
                    Props.h_code.get("method"): Props.h_code.get("while"),
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("exp"): expression,
                    Props.h_code.get("goto"): bl_name
                }
                self.__add_local(while_jump_info)

                while_info = {
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("body"): list(),
                }
                self.blocks[bl_name] = while_info
                self.stack.append(bl_name)
            
            elif(token[0] == Props.t_keywords.get("else")):
                self.__check_scope(usage="else")
                assert len(self.blocks[self.stack[-1]][Props.h_code.get("body")]) != 0, "usage of 'else' without 'if'"
                assert self.blocks[self.stack[-1]][Props.h_code.get("body")][-1].get(Props.h_code.get("method")) == Props.h_code.get("if"), "usage of 'else' without 'if'"  # todo: fix this

                bl_name = ".else" + str(uuid.uuid4().hex)
                else_jump_info = {
                    Props.h_code.get("method"): Props.h_code.get("else"),
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("goto"): bl_name
                }

                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get("{"), "expected '{'"
                self.__add_local(else_jump_info)

                else_info = {
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("body"): list(),
                }
                self.blocks[bl_name] = else_info
                self.stack.append(bl_name)

            elif(token[0] == Props.t_symbols.get("}")):
                # assert len(self.stack) != 0, "mismatched '}'"
                self.__check_scope(usage="}", message="mismatched '}'")
                self.stack.pop()

            elif(token[0] == Props.t_indentifier):
                name = token
                self.tokens.next()
                token = self.tokens.peek()
                if(token[0] == Props.t_symbols.get("=")): # assignment 
                    self.__check_scope(usage="=")

                    self.tokens.next()
                    expression_tokens = self.tokens.until()
                    expression = Build(expression_tokens).build() # todo: fix this
                    assign_info = {
                        Props.h_code.get("method"): Props.h_code.get("assign"),
                        Props.h_code.get("name"): name[2].get("raw"),
                        Props.h_code.get("line"): name[1],
                        Props.h_code.get("exp"): expression
                    }
                    assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                    self.__add_local(assign_info)

                elif(token[0] == Props.t_symbols.get("(")): #function call
                    self.__check_scope(usage="function call")

                    raw_expression = self.tokens.until()
                    raw_expression.insert(0, name)

                    expression = Build(raw_expression).build()

                    function_call_info = {
                        Props.h_code.get("method"): Props.h_code.get("fn_call"),
                        Props.h_code.get("exp"): expression,
                        Props.h_code.get("line"): name[1],
                    }
                    
                    assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                    self.__add_local(function_call_info)

            elif(token[0] == Props.t_keywords.get("pyimport")):
                self.__check_scope(usage="pyimport")
                self.tokens.next()
                name = self.tokens.peek()
                assert name[0] == Props.t_indentifier, "expected identifier"
                pyimport_info = {
                    Props.h_code.get("method"): Props.h_code.get("pyimport"),
                    Props.h_code.get("name"): name[2].get("raw"),
                    Props.h_code.get("line"): name[1],
                }
                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                self.__add_local(pyimport_info)

            elif(token[0] == Props.t_keywords.get("pycall")):
                self.__check_scope(usage="pycall")
                self.tokens.next()
                m_name = self.tokens.peek()
                assert m_name[0] == Props.t_indentifier, "expected identifier"
                self.tokens.next()
                name = self.tokens.peek()
                assert name[0] == Props.t_indentifier, "expected identifier"

                pyimport_info = {
                    Props.h_code.get("method"): Props.h_code.get("pycall"),
                    Props.h_code.get("m_name"): m_name[2].get("raw"),
                    Props.h_code.get("name"): name[2].get("raw"),
                    Props.h_code.get("line"): name[1],
                }
                self.tokens.next()
                assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                self.__add_local(pyimport_info)

            elif(token[0] == Props.t_keywords.get("pyarg")):
                # assert len(self.stack) != 0, "usage of 'ret' in global scope"
                self.__check_scope(usage="pyarg")

                self.tokens.next()
                expression_tokens = self.tokens.until()
                expression = Build(expression_tokens).build() # todo: fix this
                return_info = {
                    Props.h_code.get("method"): Props.h_code.get("pyarg"),
                    Props.h_code.get("line"): token[1],
                    Props.h_code.get("exp"): expression
                }
                assert self.tokens.peek()[0] == Props.t_symbols.get(";"), "expected ';'"
                self.__add_local(return_info)
            
            else:
                assert False, f"unknown literal" 

        return {
            Props.h_code.get("import"): list(self.imports),
            # "include": [],
            # "stack": [],
            Props.h_code.get("blocks"): self.blocks,
            Props.h_code.get("reg"): None
        }

    def __check_scope(self, usage:str, local:bool=True, message:str=None):
        if(local):
            assert len(self.stack) != 0, f"usage of '{usage}' in global scope" if message == None else message
        else:
            assert len(self.stack) == 0, f"usage of '{usage}' in local scope" if message == None else message

    def __add_local(self, inst:dict) -> None:
        local_scope = self.stack[-1]
        self.blocks[local_scope][Props.h_code.get("body")].append(inst)