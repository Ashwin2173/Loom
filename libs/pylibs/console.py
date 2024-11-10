import time
import sys

def cprint(arg:list) -> None: 
    colors = {'red': '\x1b[31m', 'green': '\x1b[32m', 'yellow': '\x1b[33m', 'blue': '\x1b[34m'}
    color = colors.get(arg[0], "\x1b[0m")
    message = arg[1]
    end = arg[2]
    reset = "\x1b[0m"
    sys.stdout.write(f"{color}{message}{end}{reset}")

def _in(arg:list) -> None: 
    return input()

def _time(t) -> None:
    return time.time()
# import sys
# def print_colored(text, color, end='\n'):
#     colors = {'red': '\x1b[31m', 'green': '\x1b[32m', 'yellow': '\x1b[33m', 'blue': '\x1b[34m'}
#     reset = '\x1b[0m'
#     sys.stdout.write(colors.get(color, '') + text + reset + end)

# print_colored('red text', color='red')
# print_colored('green text', color='green')
# print_colored('blue text', color='blue')
