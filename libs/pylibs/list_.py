def len_(lst):
    return len(lst[0])

def updateAt(lst):
    list_, index, value = lst
    list_[index] = value
    return list_

def newList(args):
    size = args[0]
    return [0] * size