import asyncio

from src.util.cputop import CPUtop
from src.util.memtop import MEMtop
from src.util import Systeminfo
from src.util.databus import sysque

cpu = CPUtop()
mem = MEMtop()

def get_sysinfo() -> Systeminfo:
    cpudata = cpu.get_cpu_info()
    memdata = mem.get_mem_info()
    return Systeminfo(
        cpu=cpudata,
        mem=memdata,
    )

async def queue_runner():
    while True:
        try:
            data = await asyncio.to_thread(get_sysinfo)
            await sysque.put(data)
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            return
        except Exception:
            continue