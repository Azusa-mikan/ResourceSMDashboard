from queue import Queue

from src.util import Systeminfo

sysque: Queue[Systeminfo] = Queue(maxsize=1)
