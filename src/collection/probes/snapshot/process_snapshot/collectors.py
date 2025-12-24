# collectors.py
from process_snapshot import ProcessSnapshot, CpuSnapshot, MemorySnapshot, _safe
import psutil

def collect_identity(proc: psutil.Process, snap: ProcessSnapshot):
    snap.identity.update({
        "ppid": proc.ppid(),
        "exe": _safe(proc.exe),
        "cmdline": _safe(proc.cmdline, []),
        "cwd": _safe(proc.cwd),
        "username": _safe(proc.username),
        "status": _safe(proc.status),
    })

def collect_cpu(proc: psutil.Process, snap: ProcessSnapshot):
    snap.cpu = CpuSnapshot(
        percent=_safe(lambda: proc.cpu_percent(interval=0.0)),
        times=_safe(proc.cpu_times),
        affinity=_safe(proc.cpu_affinity),
        cpu_num=_safe(proc.cpu_num),
    )

def collect_memory(proc: psutil.Process, snap: ProcessSnapshot):
    snap.memory = MemorySnapshot(
        percent=_safe(proc.memory_percent),
        info=_safe(proc.memory_info),
        full_info=_safe(proc.memory_full_info),
        maps=_safe(proc.memory_maps),
    )

def collect_relationships(proc: psutil.Process, snap: ProcessSnapshot):
    snap.relationships.update({
        "parents": [p.pid for p in _safe(proc.parents, [])],
        "children": [c.pid for c in _safe(proc.children, [])],
    })

DEFAULT_COLLECTORS = [
    collect_identity,
    collect_cpu,
    collect_memory,
    collect_relationships,
]
