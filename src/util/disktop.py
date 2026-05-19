import psutil
from nvitop import NA

from src.util import Volumeinfo, DiskIOinfo

class Diskinfo:
    def __init__(self) -> None:
        pass

    def get_volumes(self) -> list[Volumeinfo]:
        vols: list[Volumeinfo] = []

        for p in psutil.disk_partitions():
            u = psutil.disk_usage(p.mountpoint)

            vols.append(Volumeinfo(
                name=p.device,
                filesystem=p.fstype,
                total=u.total,
                free=u.free,
            ))
        
        return vols

    def get_disk_io(self) -> DiskIOinfo:
        i = psutil.disk_io_counters()
        if i is None:
            return DiskIOinfo(
                read_bytes=NA,
                write_bytes=NA,
            )

        return DiskIOinfo(
            read_bytes=i.read_bytes,
            write_bytes=i.write_bytes,
        )