
from nvitop import Device

from src.util import GPUMEMinfo, GPUPowerinfo, GPUinfo, GPU


class NvidiaGPU(GPU):
    def __init__(self) -> None:
        self.gpu = Device.all()[0]

    def get_gpu_info(self):
        memdata = GPUMEMinfo(
            clock=self.gpu.memory_clock(),
            total=self.gpu.memory_total(),
            used=self.gpu.memory_used(),
            free=self.gpu.memory_free()
        )
        powerdata = GPUPowerinfo(
            usage=self.gpu.power_usage(),
            max=self.gpu.power_limit(),
        )
        return GPUinfo(
            name=self.gpu.name(),
            usage=self.gpu.gpu_utilization(),
            clock=self.gpu.graphics_clock(),
            mem=memdata,
            power=powerdata,
        )