import re

from utils.props import Props

token_list = list[tuple]()
line_number = 1
left_pointer = 0
pointer = 0
program = None

def lexify():
    global program 
    program = Props.raw_program + " eof"
    global token_list
    global line_number
    global left_pointer
    global pointer

    primary_symbols = {
        ":", ";", "{", "}", "(", ")", "&", "|", "+", "-", "*", "/", ",", "[", "]"
    }

    secondary_symbols = {
        "=", ">", "<", "!", "%", "^"
    }

    while(len(program) > pointer):
        char = program[pointer]
        if(char == '"' or char == '`'):
            t_char = char
            t_previous = char
            pointer += 1
            while(len(program) > pointer and not (program[pointer] == t_char and t_previous != "\\")):
                t_previous = program[pointer]
                pointer += 1
            assert len(program) > pointer, f"lexfault: '{t_char}' without end at line {line_number}"
            pointer += 1
            add_token()
            if(program[pointer] == " " or program[pointer] == "\n"):
                left_pointer = pointer + 1
            else:
                left_pointer = pointer
        elif(char == " "):
            add_token()
            left_pointer = pointer + 1
        elif(char == "\n"):
            add_token()
            line_number += 1
            left_pointer = pointer + 1
        elif(char in primary_symbols): 
            add_token()
            left_pointer = pointer + 1
            add_token(left_offset=-1, offset=1)
        elif(char in secondary_symbols):
            add_token()
            if(program[pointer + 1] == "="):
                left_pointer = pointer + 2
                add_token(left_offset=-2, offset=2)
                pointer += 1
            else:
                left_pointer = pointer + 1 
                add_token(left_offset=-1, offset=1)
            
        pointer += 1
    return token_list

def add_token(left_offset:int=0, offset:int=0) -> None:
    raw_token = program[left_pointer+left_offset:pointer+offset]
    token = get_token(raw=raw_token, line=line_number)
    if(token != None):
        token_list.append(token)

def get_token(raw:int, line:int) -> tuple:
    type_ = None
    others = {}
    if(raw == "" or raw[0] == "`"):
        return None
    elif(raw[0] == '"'): # string literal
        others["raw"] = raw[1:-1]
        type_ = 100
    elif(re.match(r"^-?\d+$", raw)): # int literal
        others["raw"] = int(raw)
        type_ = 101
    elif(re.match(r"^-?\d*\.\d+$|^-?\d+\.\d*$", raw)): #float literal
        others["raw"] = float(raw)
        type_ = 102
    else:
        type_ = get_type(raw)
        if(type_ == 0):
            others["raw"] = raw
    assert type_ != None, f"unknown literal '{raw}' at line {line}"
    return (type_, line, others)

def get_type(raw:str) -> int:
    keywords = Props.t_keywords
    symbols = Props.t_symbols
    if(raw in keywords):
        return keywords[raw]
    if(raw in symbols):
        return symbols[raw]
    if(re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', raw)):
        return 0
        