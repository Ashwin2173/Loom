class Props:
    file_path = None
    mod_path = None
    raw_program = str()
    p_args = []
    t_keywords = {
        "import": 1,
        "fn": 2,
        "ret": 3,
        "var": 4,
        "if": 5,
        "true": 6, 
        "false": 7,
        "null": 8,
        "pyimport": 9,
        "pycall": 10,
        "pyarg": 11,
        "else": 12,
        "while": 13,
        "raise": 14
    }
    t_int_lit = 101
    t_float_lit = 102
    t_string_lit = 100
    t_indentifier = 0
    t_symbols = {
        ";": 201,
        ":": 202,
        "(": 203,
        ")": 204,
        "{": 205,
        "}": 206,
        "=": 207,
        "+": 208,
        "-": 209,
        "*": 210,
        "/": 211,
        "==": 212,
        ">=": 213,
        "<=": 214,
        ">": 215,
        "<": 216,
        "!": 217,
        "!=": 218,
        "&": 219,
        "|": 220,
        ",": 221,
        "%": 222,
        "^": 223,
        "[": 224,
        "]": 225
    }
    h_code = {
        "import": "1",
        "body": "2",
        "ret": "3",
        "args": "4",
        "reg": "5",
        "stack": "6",
        "exp": "7",
        "var": "8",
        "name": "9",
        "blocks": "10",
        "assign": "11",
        "line": "12",
        "if": "13",
        "goto": "14",
        "method": "15",
        "true": "16",
        "false": "17",
        "pyimport": "18",
        "m_name": "19",
        "pycall": "20",
        "pyarg": "21",
        "fn_call": "22",
        "else": "23",
        "while": "24",
        "raise": "25"
    }
    # h_code = {
    #     "import": "import",
    #     "body": "body",
    #     "ret": "ret",
    #     "args": "args",
    #     "reg": "reg",
    #     "stack": "stack",
    #     "exp": "exp",
    #     "var": "var",
    #     "name": "name",
    #     "blocks": "blocks",
    #     "assign": "assign",
    #     "line": "line",
    #     "if": "if",
    #     "goto": "goto",
    #     "method": "method",
    #     "true": "true",
    #     "false": "false",
    #     "pyimport": "pyimport",
    #     "m_name": "m_name",
    #     "pycall": "pycall",
    #     "pyarg": "pyarg",
    #     "fn_call": "fn_call",
    #     "else": "else",
    #     "while": "while"
    # }