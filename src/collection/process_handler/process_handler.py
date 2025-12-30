"""Process Handler."""

from collection.process_handler.audited_process import AuditedProcess
from shared.services import logger


class ProcessHandler:
    """Manages processes."""

    def __init__(self) -> None:
        """Initialise the ProcessHandler."""
        self._processes: list[AuditedProcess] = []

    def add_process(self, process: AuditedProcess) -> None:
        """Track an existing process."""
        if not isinstance(process, AuditedProcess):
            msg = "Expected an AuditedProcess instance"
            raise TypeError(msg)
        self._processes.append(process)

    def num_active(self) -> int:
        """Return the number of active processes."""
        active_count = 0
        for process in self._processes:
            try:
                if process.is_alive():
                    active_count += 1
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to check if process is alive: {e}")
        return active_count

    def get_processes(self) -> list[AuditedProcess]:
        """Return the list of all processes."""
        return self._processes

    def shutdown_all(self, *, timeout: float = 5.0, force: bool = False) -> None:
        """
        Shutdown all tracked processes safely.
        """
        for process in self._processes:
            try:
                result = process.shutdown(timeout=timeout, force=force)
                if result:
                    logger.info("Process %s shutdown successfully", process.pid)
                else:
                    logger.warning("Process %s failed to shutdown cleanly", process.pid)
            except Exception as e:
                logger.warning("Exception shutting down process %s: %s", process.pid, e)
                raise

    def remove_all(self) -> None:
        """
        Clear tracked processes.

        Warning: Does not shutdown a created process.
        """
        self._processes = []


if __name__ == "__main__":
    process_handler = ProcessHandler()
