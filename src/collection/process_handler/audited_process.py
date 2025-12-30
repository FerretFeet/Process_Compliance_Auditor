"""Audited Process."""

import contextlib
import os
import signal
import subprocess
from typing import TYPE_CHECKING

import psutil

from shared.custom_exceptions import ProcessNotCreatedError
from shared.services import logger

if TYPE_CHECKING:
    from collections.abc import Callable


class AuditedProcess:
    """Container for a psutil Process Instance."""

    def __init__(self, pid_or_command: list[str] | int) -> None:
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
            msg = "Argument must be an int (PID) or a list of command arguments"
            raise TypeError(msg)

    def is_alive(self) -> bool:
        """Check if the process is alive."""
        if not self.process:
            return False
        try:
            return self.process.is_running() and self.process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False

    def _initialize_from_pid(self) -> None:
        """Attach to an existing process using the PID."""
        if self.pid:
            try:
                self.process = psutil.Process(self.pid)
                logger.info(f"Attached to process {self.pid}")
            except psutil.NoSuchProcess as err:
                msg = f"Process with PID {self.pid} does not exist."
                logger.warning(msg)
                raise ProcessNotCreatedError(msg) from err
            except psutil.AccessDenied as err:
                msg = f"Accessed denied for process with PID {self.pid}."
                logger.warning(msg)
                raise ProcessNotCreatedError(msg) from err
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
        Shut down this process (and its children) safely.

        Returns True if all processes exited, False otherwise.
        """
        if not self.created:
            logger.info("Not shutting down external process %s", self.pid)
            return False

        if not self.process:
            return True

        try:
            # Phase 1: graceful termination
            gone, alive = self._kill_proc_tree(  # noqa: RUF059
                self.pid,
                sig=signal.SIGTERM,
                include_parent=True,
                timeout=timeout,
            )

            # Phase 2: forced termination if needed
            if alive and force:
                logger.warning(
                    "Forcing kill of remaining processes: %s",
                    [p.pid for p in alive],
                )
                _, alive = self._kill_proc_tree(
                    self.pid,
                    sig=signal.SIGKILL,
                    include_parent=True,
                    timeout=timeout,
                )

        except psutil.NoSuchProcess:
            return True

        else:
            if alive:
                logger.warning(
                    "Some processes did not exit: %s",
                    [p.pid for p in alive],
                )
                return False

            return True

    def _kill_proc_tree(
        self,
        pid: int,
        *,
        sig: signal.Signals = signal.SIGTERM,
        include_parent: bool = True,
        timeout: float | None = None,
        on_terminate: Callable[[psutil.Process], object | None] | None = None,
    ) -> tuple[list[psutil.Process], list[psutil.Process]]:
        if pid is None:
            msg = "Cannot kill process: PID is None."
            raise ValueError(msg)
        if pid == os.getpid():
            msg = "Refusing to kill the current process."
            raise RuntimeError(msg)

        try:
            parent = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return [], []

        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)

        for p in children:
            with contextlib.suppress(psutil.NoSuchProcess):
                p.send_signal(sig)

        gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
        return gone, alive
