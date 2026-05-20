from dataclasses import dataclass
from abc import ABC, abstractmethod

from nvitop import NaType

@dataclass(kw_only=True)
class CPUinfo:
    name: str
    usage: int | NaType
    clock: float | NaType
    temperature: float | NaType
    core_count: int | NaType
    thread_count: int | NaType

@dataclass(kw_only=True)
class MEMinfo:
    total: float
    available: float
    used: float
    type: str | NaType
    speed: int | NaType

@dataclass(kw_only=True)
class GPUMEMinfo:
    clock: int | NaType
    total: int | NaType
    used: int | NaType
    free: int | NaType

@dataclass(kw_only=True)
class GPUPowerinfo:
    usage: int | NaType
    max: int | NaType

@dataclass(kw_only=True)
class GPUinfo:
    name: str | NaType
    usage: int | NaType
    clock: int | NaType
    mem: GPUMEMinfo
    power: GPUPowerinfo


class GPU(ABC):
    @abstractmethod
    def get_gpu_info(self) -> GPUinfo:
        ...


@dataclass(kw_only=True)
class DiskIOinfo:
    read_bytes: int | NaType
    write_bytes: int | NaType

@dataclass(kw_only=True)
class Volumeinfo:
    name: str
    filesystem: str
    total: int
    free: int

@dataclass(kw_only=True)
class Systeminfo:
    cpu: CPUinfo
    mem: MEMinfo