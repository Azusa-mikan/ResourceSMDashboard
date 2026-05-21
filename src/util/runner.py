import asyncio

from src.util.cputop import CPUtop
from src.util.memtop import MEMtop
from src.util.sysdataclass import DynamicSysteminfo, StaticSysteminfo
from src.util.databus import sysque

cpu = CPUtop()
mem = MEMtop()

def get_dynamic_sysinfo() -> DynamicSysteminfo:
    cpudata = cpu.get_dynamic_cpu_info()
    memdata = mem.get_dynamic_mem_info()
    return DynamicSysteminfo(
        cpu=cpudata,
        mem=memdata,
    )

def get_static_sysinfo() -> StaticSysteminfo:
    cpudata = cpu.get_static_cpu_info()
    memdata = mem.get_static_mem_info()
    return StaticSysteminfo(
        cpu=cpudata,
        mem=memdata,
    )

async def queue_runner():
    while True:
        try:
            data = await asyncio.to_thread(
                get_dynamic_sysinfo
            )
            await sysque.put(data)
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            return
        except Exception:
            continue