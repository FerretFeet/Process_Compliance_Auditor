
from src.process_handler import ProcessSnapshot
from src.process_handler.audited_process import AuditedProcess
from src.services import logger


class ProcessHandler:
    """Manages processes."""
    def __init__(self):
        """Initialise the ProcessHandler."""
        self._processes: list[AuditedProcess] = []

    def add_process(self, process: AuditedProcess):
        """Track an existing process."""
        if not isinstance(process, AuditedProcess):
            raise TypeError("Expected an AuditedProcess instance")
        self._processes.append(process)

    def num_active(self) -> int:
        """Return the number of active processes."""
        active_count = 0
        for process in self._processes:
            try:
                if process.is_alive():
                    active_count += 1
            except Exception as e:
                logger.warning(f"Failed to check if process is alive: {e}")
        return active_count

    def get_snapshot(self) -> list[ProcessSnapshot]:
        """Return a snapshot of all tracked processes."""
        snapshots: list[ProcessSnapshot] = []
        for process in self._processes:
            try:
                snapshots.append(process.snapshot())
            except Exception as e:
                logger.warning(f"Failed to take snapshot for process {process}: {e}")
        return snapshots

    def shutdown_all(self) -> None:
        """Shutdown all tracked processes."""
        for process in self._processes:
            try:
                process.shutdown()
            except Exception as e:
                logger.warning(f"Failed to shutdown process {process}: {e}")


    def remove_all(self) -> None:
        self._processes = []


if __name__ == "__main__":
    process_handler = ProcessHandler()