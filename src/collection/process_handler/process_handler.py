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

    def shutdown_all(self) -> None:
        """Shutdown all tracked processes."""
        for process in self._processes:
            try:
                process.shutdown()
            except Exception as e:
                logger.warning(f"Failed to shutdown process {process}: {e}")
                raise

    def remove_all(self) -> None:
        """
        Clear tracked processes.

        Warning: Does not shutdown a created process.
        """
        self._processes = []


if __name__ == "__main__":
    process_handler = ProcessHandler()
