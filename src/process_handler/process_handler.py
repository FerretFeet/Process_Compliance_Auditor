
from src.process_handler import ProcessSnapshot
from src.process_handler.audited_process import AuditedProcess




class ProcessHandler:
    """Manages processes."""
    def __init__(self):
        """Initialise the ProcessHandler."""
        self.processes: list[AuditedProcess] = []

    def add_process(self, process: AuditedProcess):
        """Track an existing process."""
        self.processes.append(process)

    def num_active(self):
        """Return the number of active processes."""
        return sum(
            [process.is_alive() for process in self.processes]
        )

    def get_snapshot(self) -> list[ProcessSnapshot]:
        """Return a snapshot of all tracked processes."""
        return [process.snapshot() for process in self.processes]

    def shutdown_all(self):
        for process in self.processes:
            process.shutdown()

    def detach_all(self):
        self.processes = []


if __name__ == "__main__":
    process_handler = ProcessHandler()