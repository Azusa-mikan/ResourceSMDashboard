import math
import os
import platform
import re
import importlib
import subprocess
import sys
import shutil

import psutil
from nvitop import NA

from src.util import CPUinfo


def _clamp_int(value: float, min_value: int, max_value: int) -> int:
    try:
        n = int(round(float(value)))
    except Exception:
        return min_value
    return max(min_value, min(max_value, n))


def _read_text(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def _cpu_name_linux() -> str | None:
    text = _read_text("/proc/cpuinfo")
    if not text:
        return None
    for line in text.splitlines():
        if "model name" in line:
            _, _, v = line.partition(":")
            v = v.strip()
            if v:
                return v
    return None


def _cpu_name_windows() -> str | None:
    try:
        winreg = importlib.import_module("winreg")
    except Exception:
        return None

    hklm = getattr(winreg, "HKEY_LOCAL_MACHINE", None)
    open_key = getattr(winreg, "OpenKey", None)
    query_value_ex = getattr(winreg, "QueryValueEx", None)
    if hklm is None or open_key is None or query_value_ex is None:
        return None

    key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
    try:
        with open_key(hklm, key_path) as k:
            value, _ = query_value_ex(k, "ProcessorNameString")
            if isinstance(value, str):
                value = value.strip()
                return value or None
    except Exception:
        return None
    return None


def _cpu_name_macos() -> str | None:
    try:
        p = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=1.5,
        )
    except Exception:
        return None
    s = (p.stdout or "").strip()
    return s or None


def _get_cpu_name() -> str:
    if sys.platform.startswith("linux"):
        name = _cpu_name_linux()
        if name:
            return name
    elif sys.platform.startswith("win"):
        name = _cpu_name_windows()
        if name:
            return name
    elif sys.platform == "darwin":
        name = _cpu_name_macos()
        if name:
            return name

    name = platform.processor()
    if name:
        return name

    return "Unknown CPU"


def _score_temp_label(label: str) -> int:
    s = label.lower()
    if "package" in s:
        return 50
    if "tctl" in s or "tdie" in s:
        return 40
    if "die" in s:
        return 30
    if "core" in s:
        return 20
    return 10


def _get_cpu_temperature_celsius() -> float:
    try:
        temps = psutil.sensors_temperatures(fahrenheit=False) # type: ignore
    except Exception:
        temps = None

    if temps:
        candidates: list[tuple[int, float]] = []
        for _, entries in temps.items():
            for e in entries:
                cur = getattr(e, "current", None)
                if cur is None:
                    continue
                try:
                    cur_f = float(cur)
                except Exception:
                    continue
                label = getattr(e, "label", "") or ""
                candidates.append((_score_temp_label(label), cur_f))

        if candidates:
            candidates.sort(key=lambda x: (x[0], x[1]))
            return candidates[-1][1]

    if sys.platform.startswith("win"):
        best = _get_cpu_temperature_windows_acpi()
        if best is not None:
            return best

    if sys.platform.startswith("linux"):
        base = "/sys/class/thermal"
        try:
            entries = os.listdir(base)
        except Exception:
            entries = []

        best: float | None = None
        for d in entries:
            if not d.startswith("thermal_zone"):
                continue
            t_path = os.path.join(base, d, "type")
            temp_path = os.path.join(base, d, "temp")
            t = _read_text(t_path)
            v = _read_text(temp_path)
            if not v:
                continue
            try:
                raw = float(v.strip())
            except Exception:
                continue
            c = raw / 1000.0 if raw > 1000 else raw
            if not math.isfinite(c) or c <= 0:
                continue
            if t and re.search(r"(x86_pkg_temp|cpu|package|tctl|tdie)", t, re.I):
                if best is None or c > best:
                    best = c
            elif best is None:
                best = c

        if best is not None:
            return best

    return math.nan


def _get_cpu_temperature_windows_acpi() -> float | None:
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if not exe:
        return None

    perf_cmd = (
        "$ErrorActionPreference='SilentlyContinue';"
        "Get-CimInstance -Namespace root/cimv2 -ClassName Win32_PerfFormattedData_Counters_ThermalZoneInformation "
        "| ForEach-Object { if ($_.HighPrecisionTemperature) { $_.HighPrecisionTemperature } else { $_.Temperature } }"
    )

    for _ in range(2):
        try:
            p = subprocess.run(
                [exe, "-NoProfile", "-Command", perf_cmd],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
        except Exception:
            continue

        candidates: list[float] = []
        for token in (p.stdout or "").split():
            try:
                raw_f = float(token.strip())
            except Exception:
                continue
            if raw_f <= 0:
                continue
            c = raw_f / 10.0 - 273.15 if raw_f >= 1000.0 else raw_f - 273.15
            if math.isfinite(c) and (-20.0 <= c <= 130.0):
                candidates.append(c)

        if candidates:
            return max(candidates)

    return None


def _get_cpu_clock_ghz() -> float:
    f = psutil.cpu_freq()
    if f is not None and f.current:
        try:
            mhz = float(f.current)
            if mhz > 0:
                return round(mhz / 1000.0, 2)
        except Exception:
            pass

    if sys.platform.startswith("linux"):
        v = _read_text("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
        if v:
            try:
                khz = float(v.strip())
                if khz > 0:
                    return round((khz / 1000.0) / 1000.0, 2)
            except Exception:
                pass

    return 0.0


class CPUtop:
    def __init__(self) -> None:
        pass

    def get_cpu_info(self) -> CPUinfo:
        try:
            usage = _clamp_int(psutil.cpu_percent(interval=0.12), 0, 100)
        except Exception:
            usage = NA

        clock = _get_cpu_clock_ghz()
        if clock <= 0:
            clock = NA

        temperature = float(_get_cpu_temperature_celsius())
        if not math.isfinite(temperature):
            temperature = NA
        else:
            temperature = round(temperature, 1)

        core_count = int(psutil.cpu_count(logical=False) or 0)
        if core_count <= 0:
            core_count = NA

        thread_count = int(psutil.cpu_count(logical=True) or 0)
        if thread_count <= 0:
            thread_count = NA

        return CPUinfo(
            name=_get_cpu_name(),
            usage=usage,
            clock=clock,
            temperature=temperature,
            core_count=core_count,
            thread_count=thread_count,
        )
