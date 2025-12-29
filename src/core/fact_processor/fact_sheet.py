from typing import Any
from collection.process_handler import ProcessSnapshot


class FactSheet:
    """
    An interface to translate a ProcessSnapshot into a dict of audit-friendly facts.
    This normalizes and flattens data for rule_builder evaluation.
    """

    def __init__(self, snapshot: ProcessSnapshot):
        self.snapshot = snapshot
        self.facts = self._extract_facts(snapshot)

    def _extract_facts(self, snapshot: ProcessSnapshot) -> dict[str, Any]:
        """Convert a ProcessSnapshot into a flat dictionary of facts."""
        facts = {}

        # Basic process info
        facts["pid"] = snapshot.pid
        facts["ppid"] = snapshot.ppid
        facts["name"] = snapshot.name
        facts["exe"] = snapshot.exe
        facts["cmdline"] = snapshot.cmdline
        facts["cwd"] = snapshot.cwd
        facts["username"] = snapshot.username
        facts["status"] = snapshot.status
        facts["is_running"] = snapshot.is_running
        facts["snapshot_time"] = snapshot.snapshot_time

        # Parent/child relationships
        facts["parent_pids"] = snapshot.parents
        facts["num_children"] = len(snapshot.children)
        facts["child_pids"] = snapshot.children

        # CPU info
        facts["cpu_num"] = snapshot.cpu_num
        facts["cpu_percent"] = snapshot.cpu_percent
        facts["cpu_times_user"] = snapshot.cpu_times.user if snapshot.cpu_times else None
        facts["cpu_times_system"] = snapshot.cpu_times.system if snapshot.cpu_times else None
        facts["cpu_affinity"] = snapshot.cpu_affinity

        # Memory info
        facts["memory_rss_mb"] = (
            snapshot.memory_info.rss / 1024**2 if snapshot.memory_info else None
        )
        facts["memory_vms_mb"] = (
            snapshot.memory_info.vms / 1024**2 if snapshot.memory_info else None
        )
        facts["memory_percent"] = snapshot.memory_percent
        facts["num_memory_maps"] = len(snapshot.memory_maps) if snapshot.memory_maps else 0

        # I/O
        facts["io_read_count"] = snapshot.io_counters.read_count if snapshot.io_counters else None
        facts["io_write_count"] = snapshot.io_counters.write_count if snapshot.io_counters else None
        facts["io_read_bytes"] = snapshot.io_counters.read_bytes if snapshot.io_counters else None
        facts["io_write_bytes"] = snapshot.io_counters.write_bytes if snapshot.io_counters else None

        # Threads and file descriptors
        facts["num_threads"] = snapshot.num_threads
        facts["num_fds"] = snapshot.num_fds
        facts["num_ctx_switches_voluntary"] = (
            snapshot.num_ctx_switches[0] if snapshot.num_ctx_switches else None
        )
        facts["num_ctx_switches_involuntary"] = (
            snapshot.num_ctx_switches[1] if snapshot.num_ctx_switches else None
        )
        facts["num_open_files"] = len(snapshot.open_files) if snapshot.open_files else 0

        # Network connections
        facts["num_net_connections"] = (
            len(snapshot.net_connections) if snapshot.net_connections else 0
        )

        # Security identifiers
        facts["uids"] = snapshot.uids
        facts["gids"] = snapshot.gids

        # Limits
        facts["rlimits"] = snapshot.rlimit

        # Derived/normalized facts
        facts["thread_ids"] = [t.id for t in snapshot.threads] if snapshot.threads else []
        facts["open_file_paths"] = (
            [f.path for f in snapshot.open_files] if snapshot.open_files else []
        )

        return facts

    def get(self, key: str, default=None) -> Any:
        """Get a fact by key."""
        return self.facts.get(key, default)

    def as_dict(self) -> dict[str, Any]:
        """Return the full fact dictionary."""
        return self.facts
