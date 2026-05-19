from src.util.gputop import NvidiaGPU

gpu = NvidiaGPU()

print(gpu.get_gpu_info())