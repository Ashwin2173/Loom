class WalkError(Exception):
    pass

class PythonError(Exception):
    pass

class CustomError(Exception):
    def __init__(self, error_name:str, message:str) -> None:
        super().__init__(message)
        self.error_name = error_name


class ExpressionError(Exception):
    pass

class VariableError(Exception): 
    pass 