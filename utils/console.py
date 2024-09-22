from colorama import Fore

def log(arg):
    print(f"{arg}")

def error(arg):
    print(f"{Fore.RED}{arg}{Fore.RESET}")

def info(arg):
    print(f"{Fore.BLUE}{arg}{Fore.RESET}")

def warn(arg):
    print(f"{Fore.YELLOW}{arg}{Fore.RESET}")