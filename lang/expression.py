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
                raise ExpressionError(f"Invalid token for expression")
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
                    self.stack.append(f'"{value}"')
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
                    self.stack.append(f'"{value}"')
                else:
                    self.stack.append(str(value))
            else:
                self.stack.append(token[1])

        try:
            return eval(" ".join(self.stack))
        except Exception as error:
            raise ExpressionError(error)

"""class Build():
    def __init__(self, tokens:list) -> None:
        self.tokens = tokens
        self.precedence = {
            Props.t_symbols.get('|'): 7, 
            Props.t_symbols.get('&'): 6, 
            Props.t_symbols.get('!='): 5,
            Props.t_symbols.get('=='): 5, 
            Props.t_symbols.get('>='): 4, 
            Props.t_symbols.get('>'): 4, 
            Props.t_symbols.get('<='): 4, 
            Props.t_symbols.get('<'): 4, 
            Props.t_symbols.get('+'): 3, 
            Props.t_symbols.get('-'): 3, 
            Props.t_symbols.get('*'): 2, 
            Props.t_symbols.get('/'): 2,
            Props.t_symbols.get('!'): 1 
        }
        self.associativity = { 
            Props.t_symbols.get('|'): 'L',
            Props.t_symbols.get('&'): 'L', 
            Props.t_symbols.get('!='): 'L', 
            Props.t_symbols.get('=='): 'L', 
            Props.t_symbols.get('>='): 'L',
            Props.t_symbols.get('>'): 'L', 
            Props.t_symbols.get('<='): 'L', 
            Props.t_symbols.get('<'): 'L', 
            Props.t_symbols.get("+"): 'L', 
            Props.t_symbols.get('-'): 'L', 
            Props.t_symbols.get('*'): 'L', 
            Props.t_symbols.get('/'): 'L',
            Props.t_symbols.get('!'): 'R', 
        }

    def __get_precedence(self, token:list) -> int:
        return self.precedence.get(token[0], -1)
    
    def __is_left_associative(self, token:list) -> bool:
        return self.associativity.get(token[0], "L") == "L"

    def build(self):
        output = list()
        stack = list()

        for token in self.tokens:
            if(token[0] == Props.t_indentifier or token[0] == Props.t_int_lit or token[0] == Props.t_float_lit):
                output.append(token)
            elif(token[0] in self.precedence):
                while(stack and stack[-1][0] != Props.t_symbols.get("(") and 
                      (self.__get_precedence(stack[-1]) > self.__get_precedence(token) or 
                       (self.__get_precedence(stack[-1]) == self.__get_precedence(token) and self.__is_left_associative(token)))):
                    output.append(stack.pop())
                stack.append(token)
            elif(token[0] == Props.t_symbols.get("(")):
                stack.append(token)
            elif(token[0] == Props.t_symbols.get(")")):
                while(stack and stack[-1][0] != Props.t_symbols.get("(")):
                    output.append(stack.pop())
                stack.pop()
            else:
                assert False, f"Invalid token '{token[0]}'"
        
        while(stack):
            output.append(stack.pop())
        return output
    
class Execute():
    def __init__(self, tokens:list) -> None:
        self.expression = tokens
        self.stack = list()

    def execute(self):
        for token in self.expression:
            if(token[0] == Props.t_int_lit):        # todo: fix this; add variables to this conditions
                value = token[2].get("raw")
                self.stack.append(int(value))
            elif(token[0] == Props.t_float_lit):
                value = token[2].get("raw")
                self.stack.append(float(value))
            
            elif(token[0] == Props.t_symbols.get("!")):
                a = self.stack.pop()
                self.stack.append(not bool(a))
            else:
                b = self.stack.pop()
                a = self.stack.pop()
                if(token[0] == Props.t_symbols.get("&")):
                    assert (type(a) == bool and type(b) == bool), "invalid expr"
                    self.stack.append(a and b)
                elif(token[0] == Props.t_symbols.get("|")):
                    assert (type(a) == bool and type(b) == bool), "invalid expr"
                    self.stack.append(a or b)
                elif(token[0] == Props.t_symbols.get("+")):
                    self.stack.append(a + b)
                elif(token[0] == Props.t_symbols.get("-")):
                    self.stack.append(a - b)
                elif(token[0] == Props.t_symbols.get("*")):
                    self.stack.append(a * b)
                elif(token[0] == Props.t_symbols.get("/")):
                    self.stack.append(a / b)
                elif(token[0] == Props.t_symbols.get("==")):
                    self.stack.append(a == b)
                elif(token[0] == Props.t_symbols.get("<")):
                    self.stack.append(a < b)
                elif(token[0] == Props.t_symbols.get(">")):
                    self.stack.append(a > b)
                elif(token[0] == Props.t_symbols.get("<=")):
                    self.stack.append(a <= b)
                elif(token[0] == Props.t_symbols.get(">=")):
                    self.stack.append(a >= b)
                elif(token[0] == Props.t_symbols.get("!=")):
                    self.stack.append(a != b)
                else:
                    raise Exception(f"idk wtf is '{token}'!?")
        return self.stack[0]"""