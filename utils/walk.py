from utils.props import Props
from utils.error import WalkError

class Walk: 
    def __init__(self, items:list):
        self.items = items
        self.pointer = -1

    def prev(self) -> bool:
        self.pointer -=1
        return self.pointer >= 0

    def next(self) -> bool:
        self.pointer += 1
        return self.pointer < len(self.items)
    
    def peek(self, offset:int=0) -> any:
        if(self.pointer + offset >= len(self.items)):
            raise WalkError("walkfault") 
        return self.items[self.pointer + offset]

    def until(self, target:list=[Props.t_symbols.get(";")], assertion=[], stack=False) -> list:
        if(stack):
            target = [Props.t_symbols.get(")")] # stack can be only used for circle brackets currently; if required fix this
            t_param_stack = [(Props.t_symbols.get("("), self.items[self.pointer][1], {})]
            t_items = list()

            while t_param_stack: 
                item = self.items[self.pointer]
                if(item[0] == Props.t_symbols.get("(")):
                    t_param_stack.append(item)
                elif(item[0] == Props.t_symbols.get(")")):
                    assert len(t_param_stack) != 0, "walk 't_param_stack' underflow"
                    t_param_stack.pop()
                if(len(assertion) != 0):
                    assert item[0] in assertion, "walk assertion failed"
                t_items.append(item)
                self.pointer += 1

            t_items.pop()
            return t_items
        else:
            # print("---")
            t_items = list()
            while self.items[self.pointer][0] not in target: 
                # print(self.items[self.pointer])
                item = self.items[self.pointer]
                if(len(assertion) != 0):
                    assert item[0] in assertion, "walk assertion failed"
                t_items.append(item)
                self.pointer += 1
            return t_items