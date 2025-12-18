import os
import signal
import subprocess

import psutil

from src.process_handler import ProcessSnapshot
from src.services import logger


class AuditedProcess:
    """Container for a psutil Process Instance."""
    def __init__(self, pid_or_command: list[str] | int):
        """
        Initialize the AuditedProcess.
        - If `pid_or_command` is an int, attach to an existing process using its PID.
        - If `pid_or_command` is a list of strings, spawn a new process using the command.
        """
        self.process: psutil.Process | None = None
        self.pid = None
        created: bool = False
        if isinstance(pid_or_command, int):
            self.pid = pid_or_command
            self._initialize_from_pid()
        elif isinstance(pid_or_command, list):
            self._initialize_from_command(pid_or_command)
            self.created = True
        else:
            raise ValueError("Argument must be an int (PID) or a list of command arguments")

    def is_alive(self) -> bool:
        """Check if the process is alive."""
        return self.process.is_running()

    def _initialize_from_pid(self):
        """Attach to an existing process using the PID."""
        if self.pid:
            try:
                self.process = psutil.Process(self.pid)
                logger.info(f"Attached to process {self.pid}")
            except psutil.NoSuchProcess:
                logger.warning(f"Process with PID {self.pid} does not exist.")
                self.process = None
            except psutil.AccessDenied:
                logger.warning(f"Accessed denied for process with PID {self.pid}.")
                self.process = None
        else:
            logger.warning("PID is not set. Cannot initialize process.")

    def _initialize_from_command(self, command: list[str]) -> None:
        """Spawn a new process using the command."""
        self.process = psutil.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.pid = self.process.pid


    def shutdown(self):
        """Shut down the process (either by PID or a spawned process)."""
        self._kill_proc_tree(self.pid)

    def _kill_proc_tree(self, pid, sig=signal.SIGTERM, include_parent=True,
                       timeout=None, on_terminate=None):
        """Kill a process tree (including grandchildren) with signal
        "sig" and return a (gone, still_alive) tuple.
        "on_terminate", if specified, is a callback function which is
        called as soon as a child terminates.
        """
        assert pid != os.getpid(), "won't kill myself"
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        for p in children:
            try:
                p.send_signal(sig)
            except psutil.NoSuchProcess:
                pass
        gone, alive = psutil.wait_procs(children, timeout=timeout,
                                        callback=on_terminate)
        return gone, alive

    def snapshot(self) -> ProcessSnapshot:
        """Get available data from the process."""
        def _safe(callable_attr, default=None):
            """Helper to safely call psutil attributes that may raise exceptions."""
            try:
                if callable(callable_attr):
                    return callable_attr()
                return callable_attr
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                return default
        proc = self.process
        try:
            with proc.oneshot():
                return ProcessSnapshot(
                    pid=proc.pid,
                    ppid=proc.ppid(),
                    name=proc.name(),
                    exe=_safe(proc.exe),
                    cmdline=_safe(proc.cmdline, default=[]),
                    environ=_safe(proc.environ),
                    create_time=proc.create_time(),
                    as_dict=proc.as_dict(attrs=None, ad_value=None),
                    parents=[p.pid for p in proc.parents()],
                    status=proc.status(),
                    cwd=_safe(proc.cwd),
                    username=_safe(proc.username),
                    uids=_safe(proc.uids),
                    gids=_safe(proc.gids),
                    rlimit=_safe(proc.rlimit),
                    io_counters=_safe(proc.io_counters),
                    num_ctx_switches=_safe(proc.num_ctx_switches),
                    num_fds=_safe(proc.num_fds),
                    num_threads=proc.num_threads(),
                    threads=_safe(proc.threads, default=[]),
                    cpu_times=_safe(proc.cpu_times),
                    cpu_percent=proc.cpu_percent(interval=0.1),
                    cpu_affinity=_safe(proc.cpu_affinity),
                    cpu_num=_safe(proc.cpu_num),
                    memory_info=_safe(proc.memory_info),
                    memory_full_info=_safe(proc.memory_full_info),
                    memory_maps=_safe(proc.memory_maps, default=[]),
                    memory_percent=proc.memory_percent(),
                    children=[c.pid for c in _safe(proc.children, default=[])],
                    open_files=_safe(proc.open_files, default=[]),
                    net_connections=_safe(proc.connections, default=[]),
                    is_running=proc.is_running(),
                    snapshot_time=psutil.boot_time() + proc.create_time()
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Failed to snapshot process {proc.pid}: {e}")
            return None

