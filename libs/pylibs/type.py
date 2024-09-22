def _type(args):
    types = {
        str: "string",
        int: "integer",
        float: "float",
        list: "list"
    }
    if(args[0] == None):
        return "null"
    return types.get(type(args[0]), "unknown")

def _str(args):
    return str(args[0])

def _int(args):
    try:
        return int(args[0])
    except:
        return None

def _float(args):
    try:
        return float(args[0])
    except:
        return None