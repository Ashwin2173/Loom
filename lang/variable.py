from utils.error import VariableError
class Variable:
    def __init__(self, block_name:str) -> None:
        self.pool = dict()
        self.block_name = block_name

    def __parser(self, variable_name:str) -> str:
        t_variable_name = variable_name.split(".", 1)
        if(len(t_variable_name) == 2):
            scope, name = t_variable_name
            assert self.block_name == scope, "global variable not implemented"
            return name
        return variable_name

    def __check_vairable(self, variable_name:str) -> None: 
        return variable_name in self.pool

    def create(self, variable_name:str) -> None:
        variable_name = self.__parser(variable_name)
        # if(self.__check_vairable(variable_name)): 
        #     raise VariableError(f"redeclaration of the vairable '{variable_name}'")
        self.pool[variable_name] = None
    
    def get(self, variable_name:str) -> any:
        variable_name = self.__parser(variable_name)
        if(not self.__check_vairable(variable_name=variable_name)):
            raise VariableError(f"access before defination for variable '{variable_name}'")
        return self.pool.get(variable_name)
    
    def set(self, variable_name:str, value:any) -> None: 
        variable_name = self.__parser(variable_name)
        if(not self.__check_vairable(variable_name=variable_name)):
            raise VariableError(f"access before defination for variable '{variable_name}'")
        self.pool[variable_name] = value