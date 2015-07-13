import logging
import sys
from colorama import Fore, Style

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ft = (Fore.GREEN + '[%(levelname)s] %(asctime)s: ' + Fore.RESET + '%(message)s')
formatter = logging.Formatter(ft)
ch.setFormatter(formatter)
logger.addHandler(ch)

def getLogger():
    return logger
