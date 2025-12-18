from dataclasses import dataclass
from typing import Optional, Any

import psutil


@dataclass(frozen=True, slots=True)
class ProcessSnapshot:
    """Snapshot data of a psutil Process instance."""
    pid: int
    ppid: int
    name: str
    exe: Optional[str]
    cmdline: list[str]
    environ: Optional[dict[str, str]]
    create_time: float
    as_dict: dict[str, Any]
    parents: list[int]
    status: str
    cwd: Optional[str]
    username: Optional[str]
    uids: Optional[tuple[int, int, int]]
    gids: Optional[tuple[int, int, int]]
    rlimit: Optional[list[tuple]]
    io_counters: Optional[psutil._common.pio]
    num_ctx_switches: Optional[tuple[int,int]]
    num_fds: Optional[int]
    num_threads: int
    threads: list[psutil._common.pthread]
    cpu_times: psutil._common.pcputimes
    cpu_percent: float
    cpu_affinity: Optional[list[int]]
    cpu_num: Optional[int]
    memory_info: Any
    memory_full_info: Optional[Any]
    memory_maps: Optional[list[Any]]
    memory_percent: float
    children: list[int]
    open_files: list[psutil._common.popenfile]
    net_connections: list[psutil._common.pconn]
    is_running: bool
    snapshot_time: float
