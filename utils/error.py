class WalkError(Exception):
    pass

class PythonError(Exception):
    pass

class CustomError(Exception):
    def __init__(self, error_name:str, message:str) -> None:
        super().__init__(message)
        self.error_name = error_name


class ExpressionError(Exception):
    def __init__(self, message:str, expression:str=None):
        super().__init__(message)
        self.expression = "" if expression == None else expression

class VariableError(Exception): 
    pass 