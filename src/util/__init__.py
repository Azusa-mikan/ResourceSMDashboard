from abc import ABC, abstractmethod

from src.util.sysdataclass import (
    DynamiCPUinfo,
    StatiCPUinfo,
    DynamicMEMinfo,
    StaticMEMinfo,
)

class CPU(ABC):
    @abstractmethod
    def get_dynamic_cpu_info(self) -> DynamiCPUinfo:
        ...
    
    @abstractmethod
    def get_static_cpu_info(self) -> StatiCPUinfo:
        ...

class Memory(ABC):
    @abstractmethod
    def get_dynamic_mem_info(self) -> DynamicMEMinfo:
        ...
    
    @abstractmethod
    def get_static_mem_info(self) -> StaticMEMinfo:
        ...