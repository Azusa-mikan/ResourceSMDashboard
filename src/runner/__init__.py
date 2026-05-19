import threading
import queue

from src.util.databus import sysque
from src.util import Systeminfo
from src.util.cputop import CPUtop
from src.util.disktop import Diskinfo

bus = threading.Event()
cpu = CPUtop()
disk = Diskinfo()

def _put_data(data: Systeminfo):
    try:
        sysque.put_nowait(data)
        return
    except queue.Full:
        try:
            sysque.get_nowait()
        except queue.Empty:
            pass

def loop_get_info():
    while not bus.is_set():
        cpudata = cpu.get_cpu_info()
        _put_data(Systeminfo(cpu=cpudata))
        bus.wait(timeout=1)