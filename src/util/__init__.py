from dataclasses import dataclass
from abc import ABC, abstractmethod

from nvitop import NaType

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