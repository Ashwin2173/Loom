from utils.props import Props
from utils.error import ExpressionError
from lang.variable import Variable

class Build():
    def __init__(self, tokens:list) -> None:
        """ todo: fix this class; do infix to postfix """
        self.tokens = tokens

    def build(self):
        exp_tokens = list()
        exp_symbols = {
            Props.t_symbols.get("+"): "+",
            Props.t_symbols.get("-"): "-",
            Props.t_symbols.get("*"): "*",
            Props.t_symbols.get("/"): "/",
            Props.t_symbols.get("%"): "%",
            Props.t_symbols.get("^"): "**",
            Props.t_symbols.get("("): "(",
            Props.t_symbols.get(")"): ")",
            Props.t_symbols.get("["): "[",
            Props.t_symbols.get("]"): "]",
            Props.t_symbols.get(","): ",",
            Props.t_symbols.get("=="): "==",
            Props.t_symbols.get(">="): ">=",
            Props.t_symbols.get("<="): "<=",
            Props.t_symbols.get(">"): ">",
            Props.t_symbols.get("<"): "<",
            Props.t_symbols.get("!"): "not",
            Props.t_symbols.get("!="): "!=",
            Props.t_symbols.get("&"): "and",
            Props.t_symbols.get("|"): "or",
            Props.t_keywords.get("true"): "True",
            Props.t_keywords.get("false"): "False",
            Props.t_keywords.get("null"): "None"
        }

        i = 0
        while(i < len(self.tokens)):
            item = self.tokens[i]
            if(item[0] == Props.t_indentifier):
                name = item[2].get("raw")
                if(i + 1 < len(self.tokens) and self.tokens[i + 1][0] == Props.t_symbols.get("(")): # function call
                    i += 2
                    arguments = list()
                    buffer_token = list()
                    parm_stack = ["("]
                    while len(parm_stack) != 0:
                        item = self.tokens[i]
                        if(item[0] == Props.t_symbols.get("(")):
                            buffer_token.append(item)
                            parm_stack.append("(")
                        elif(item[0] == Props.t_symbols.get("[")):
                            buffer_token.append(item)
                            parm_stack.append("[")
                        elif(item[0] == Props.t_symbols.get(")")):
                            if(len(parm_stack) == 1):
                                if(len(buffer_token) != 0):
                                    arguments.append(
                                        Build(buffer_token).build()
                                    )
                                exp_tokens.append(["fc", name, arguments])
                                parm_stack.pop()
                                break
                            else:
                                buffer_token.append(item)
                                parm_stack.pop() 
                        elif(item[0] == Props.t_symbols.get("]")):
                            if(parm_stack[-1] != "["):
                                raise ExpressionError(f"Invalid expression")
                            buffer_token.append(item)
                            parm_stack.pop()
                        elif(item[0] == Props.t_symbols.get(",") and len(parm_stack) == 1):
                            arguments.append(
                                Build(buffer_token).build()
                            )
                            buffer_token = list()
                        else:
                            buffer_token.append(item)
                        i += 1
                else: # normal variable
                    exp_tokens.append(["i", name])
            elif(item[0] == Props.t_string_lit):
                exp_tokens.append(['s', f'"{item[2].get("raw")}"'])
            elif(item[0] in exp_symbols):
                exp_tokens.append(["d", exp_symbols.get(item[0])])
            elif(item[0] in {Props.t_int_lit, Props.t_float_lit}):
                exp_tokens.append(["r", str(item[2].get("raw"))])
            else:
                raise ExpressionError(f"Invalid token for expression [ERR: {item[0]}]")
            i += 1
        return exp_tokens

    
class Execute():
    def __init__(self, tokens:list, variable_pool:Variable) -> None:
        """ todo: fix this class; do postfix to answer """
        self.tokens = tokens
        self.stack = list()
        self.variable_pool = variable_pool

    def run(self):
        for token in self.tokens:
            if(token[0] == "i"):
                value = None
                if(token[1] == "reg"):
                    from lang.executer import Orchestrator
                    value = Orchestrator.get_reg()
                else:
                    value = self.variable_pool.get(token[1])
                if(type(value) == str):
                    value = value.replace("'", "\\'")
                    self.stack.append(f"'{value}'")
                else:
                    self.stack.append(str(value))
            elif(token[0] == "fc"):
                from lang.executer import Orchestrator
                name = token[1]
                arguments = token[2]
                post_args = list()
                for index in range(len(arguments)):
                    post_args.append(
                        Execute(
                            tokens = arguments[index],
                            variable_pool = self.variable_pool
                        ).run()
                    )
                value = Orchestrator.block_in(
                    block_name = name,
                    args = post_args
                )
                if(type(value) == str):
                    value = value.replace("'", "\\'")
                    self.stack.append(f"'{value}'")
                else:
                    self.stack.append(str(value))
            else:
                self.stack.append(token[1].replace("'", "\\'"))
        final_expression = " ".join(self.stack)
        try:
            return eval(final_expression)
        except Exception as error:
            raise ExpressionError(error, final_expression)
