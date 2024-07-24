from time import sleep
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

def progress(percent=0, width=30):

    hashes = width * percent // 100
    blanks = width - hashes

    print('\r[', Fore.GREEN + hashes*'░', blanks*' ', ']', f' {percent:.0f}%', sep='',
        end='', flush=True)
    
def run_loading_animation():
    for i in range(101):
        progress(i)
        sleep(0.1)

if __name__ == '__main__':
    run_loading_animation()