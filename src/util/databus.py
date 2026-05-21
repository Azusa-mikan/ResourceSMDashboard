from asyncio import Queue

from src.util.sysdataclass import DynamicSysteminfo

sysque: Queue[DynamicSysteminfo] = Queue(maxsize=1)
