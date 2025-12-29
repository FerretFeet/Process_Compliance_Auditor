import os
import signal
import subprocess
from typing import Callable

import psutil

from shared.custom_exceptions import ProcessNotCreatedException
from core.probes.snapshot import DEFAULT_COLLECTORS
from core.probes.snapshot import ProcessSnapshot, _safe
from shared.services import logger


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
        self.created = False
        if isinstance(pid_or_command, int):
            self.pid = pid_or_command
            self._initialize_from_pid()
        elif isinstance(pid_or_command, list):
            self._spawn_process(pid_or_command)
        else:
            raise ValueError("Argument must be an int (PID) or a list of command arguments")

    def is_alive(self) -> bool:
        """Check if the process is alive."""
        if not self.process:
            return False
        try:
            return self.process.is_running() and self.process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False

    def _initialize_from_pid(self):
        """Attach to an existing process using the PID."""
        if self.pid:
            try:
                self.process = psutil.Process(self.pid)
                logger.info(f"Attached to process {self.pid}")
            except psutil.NoSuchProcess as err:
                msg = f"Process with PID {self.pid} does not exist."
                logger.warning(msg)
                raise ProcessNotCreatedException(msg)
            except psutil.AccessDenied as err:
                msg = f"Accessed denied for process with PID {self.pid}."
                logger.warning(msg)
                raise ProcessNotCreatedException(msg)
        else:
            logger.warning("PID is not set. Cannot initialize process.")

    def _spawn_process(self, command: list[str]) -> None:
        """Spawn a new process using the command."""
        self.process = psutil.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.created = True
        self.pid = self.process.pid

    def shutdown(self, *, timeout: float = 5.0, force: bool = False) -> bool:
        """
        Shut down the process if it was created by this auditor.

        Returns True if the process exited, False otherwise.
        """
        if not self.created:
            logger.info(f"Not shutting down external process {self.pid}")
            return False

        if not self.process:
            return True

        try:
            # Phase 1: graceful termination
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
                return True
            except psutil.TimeoutExpired:
                if not force:
                    logger.warning(
                        f"Process {self.pid} did not exit within {timeout}s"
                    )
                    return False

            # Phase 2: forced termination
            logger.warning(f"Forcing kill of process {self.pid}")
            self.process.kill()
            self.process.wait(timeout=timeout)
            return True

        except psutil.NoSuchProcess:
            return True

    def _kill_proc_tree(self, pid, *, sig: signal.Signals =signal.SIGTERM, include_parent: bool=True,
                       timeout:float=None, on_terminate:Callable[[psutil.Process], object | None]=None):
        """Kill a process tree (including grandchildren) with signal
        "sig" and return a (gone, still_alive) tuple.
        "on_terminate", if specified, is a callback function which is
        called as soon as a child terminates.
        """
        if pid is None:
            raise ValueError("Cannot kill process: PID is None")
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


    def ____snapshot(self, collectors=None) -> ProcessSnapshot | None:
        proc = self.process
        if not proc:
            return None

        collectors = collectors or DEFAULT_COLLECTORS

        try:
            with proc.oneshot():
                snap = ProcessSnapshot(
                    pid=proc.pid,
                    name=proc.name(),
                    create_time=proc.create_time(),
                    is_running=proc.is_running(),
                )

                for collect in collectors:
                    try:
                        collect(proc, snap)
                    except Exception as e:
                        logger.debug(f"Collector failed: {collect.__name__}: {e}")

                snap.raw = _safe(lambda: proc.as_dict(attrs=None), {})
                return snap

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Snapshot failed for PID {proc.pid}: {e}")
            return None
