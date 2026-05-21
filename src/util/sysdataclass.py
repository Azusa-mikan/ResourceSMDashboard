from dataclasses import dataclass

from nvitop import NaType

@dataclass(slots=True, kw_only=True)
class DynamiCPUinfo:
    usage: int | NaType
    clock: float | NaType
    temperature: float | NaType

@dataclass(slots=True, kw_only=True)
class StatiCPUinfo:
    name: str
    core_count: int | NaType
    thread_count: int | NaType

@dataclass(slots=True, kw_only=True)
class DynamicMEMinfo:
    total: float
    available: float
    used: float

@dataclass(slots=True, kw_only=True)
class StaticMEMinfo:
    type: str | NaType
    speed: int | NaType

@dataclass(slots=True, kw_only=True)
class DynamicSysteminfo:
    cpu: DynamiCPUinfo
    mem: DynamicMEMinfo

@dataclass(slots=True, kw_only=True)
class StaticSysteminfo:
    cpu: StatiCPUinfo
    mem: StaticMEMinfo