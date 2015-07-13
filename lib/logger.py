import logging
import sys
from colorama import Fore, Style

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ft = (Fore.GREEN + '%(asctime)s: ' + Fore.BLUE + '[%(levelname)s - s%(name)s] '
      + Fore.RED + '%(message)s')
formatter = logging.Formatter(ft)
ch.setFormatter(formatter)
logger.addHandler(ch)

def getLogger():
    return logger
