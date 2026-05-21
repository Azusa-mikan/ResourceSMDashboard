import json
import re
import subprocess
import sys
import psutil

from nvitop import NA

from src.util import Memory
from src.util.sysdataclass import DynamicMEMinfo, StaticMEMinfo

MEM_TYPE: dict[int, str]  = {
    18: "SDRAM",
    20: "DDR",
    21: "DDR2",
    22: "DDR2 FB-DIMM",
    24: "DDR3",
    26: "DDR4",
    27: "LPDDR",
    28: "LPDDR2",
    29: "DDR5",
    30: "LPDDR3",
    31: "LPDDR4",
    32: "LRDIMM",
    33: "HBM",
    34: "LPDDR5",
    35: "LPDDR5X",
    36: "HBM2",
    37: "HBM2E",
    38: "HBM3",
    39: "HBM3E",
    40: "DDR6",
    41: "LPDDR6",
    42: "CAMM2"
}

def _parse_dmidecode_memory_type_and_speed(text: str):
    hw_type = NA
    speeds: list[int] = []

    devices = re.split(r"(?m)^Handle\s+0x", text)
    for device in devices:
        if "DMI type 17" not in device or "Memory Device" not in device:
            continue

        size_match = re.search(r"^\s*Size:\s*(.+)$", device, re.MULTILINE)
        if not size_match:
            continue
        size_value = size_match.group(1).strip()
        if (
            "No Module Installed" in size_value
            or size_value.upper() == "UNKNOWN"
            or size_value == "0 MB"
        ):
            continue

        type_match = re.search(r"^\s*Type:\s*(.+)$", device, re.MULTILINE)
        if type_match:
            v = type_match.group(1).strip()
            token = (v.split() or [""])[0]
            if token and token.upper() != "UNKNOWN":
                hw_type = token

        def _parse_speed(field_name: str) -> int | None:
            m = re.search(
                rf"^\s*{re.escape(field_name)}:\s*(\d+)\s*(MT/s|MHz|GT/s)\b",
                device,
                re.MULTILINE | re.IGNORECASE,
            )
            if not m:
                return None
            value = int(m.group(1))
            unit = m.group(2).lower()
            if unit == "gt/s":
                return value * 1000
            return value

        speed = _parse_speed("Configured Memory Speed")
        if speed is None:
            speed = _parse_speed("Speed")
        if speed is not None:
            speeds.append(speed)

    hw_speed = min(speeds) if speeds else NA
    return hw_type, hw_speed


class MEMtop(Memory):
    def __init__(self) -> None:
        pass

    def get_dynamic_mem_info(self) -> DynamicMEMinfo:
        vm = psutil.virtual_memory()
        total_gb = round((vm.total / (1024**3)), 1)
        avail_gb = round((vm.available / (1024**3)), 1)
        used_gb = round((total_gb - avail_gb), 1)

        return DynamicMEMinfo(
            total=total_gb,
            available=avail_gb,
            used=used_gb,
        )

    def get_static_mem_info(self) -> StaticMEMinfo:
        hw_type = NA
        hw_speed = NA

        try:
            if sys.platform.startswith("win"):
                ps_cmd = (
                    "powershell -NoProfile -Command "
                    "\"Get-CimInstance Win32_PhysicalMemory | "
                    "Select-Object Speed, SMBIOSMemoryType | ConvertTo-Json\""
                )
                out = subprocess.check_output(ps_cmd, shell=True, text=True, errors="ignore").strip()
                
                data = json.loads(out)
                mem_chips = data if isinstance(data, list) else [data]
                chip: dict = mem_chips[0]
                
                hw_type = MEM_TYPE.get(
                    chip.get("SMBIOSMemoryType", 0),
                    NA,
                )
                hw_speed = chip.get("Speed", NA)
            
            elif sys.platform.startswith("linux"):
                out = subprocess.check_output(
                    "dmidecode -t memory",
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                hw_type, hw_speed = _parse_dmidecode_memory_type_and_speed(out)
        except Exception:
            pass

        return StaticMEMinfo(
            type=hw_type,
            speed=hw_speed,
        )