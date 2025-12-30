"""Facts available from a psutil Process."""

from core.rules_engine.model.rule import SourceEnum
from shared._common.facts import FactSpec
from shared._common.operators import BOOL_OPS, COLLECTION_OPS, NUMERIC_OPS, STRING_OPS, STRUCT_OPS

PROCESS_FACTS = [
    FactSpec("pid", int, SourceEnum.PROCESS, "...", NUMERIC_OPS),
    FactSpec("name", str, SourceEnum.PROCESS, "...", STRING_OPS),
    FactSpec("create_time", float, SourceEnum.PROCESS, "...", NUMERIC_OPS),
    FactSpec("snapshot_time", float, SourceEnum.PROCESS, "...", NUMERIC_OPS),
    FactSpec("is_running", bool, SourceEnum.PROCESS, "...", BOOL_OPS),
    FactSpec("cpu", dict, SourceEnum.PROCESS, "CPU snapshot", STRUCT_OPS),
    FactSpec("cpu.percent", float, SourceEnum.PROCESS, "CPU usage", NUMERIC_OPS),
    FactSpec("cpu.cpu_num", int, SourceEnum.PROCESS, "CPU number", NUMERIC_OPS),
    FactSpec("cpu.affinity", list, SourceEnum.PROCESS, "CPU affinity", COLLECTION_OPS),
    FactSpec("cpu.times", object, SourceEnum.PROCESS, "CPU timing data", STRUCT_OPS),
    FactSpec("memory", dict, SourceEnum.PROCESS, "Memory snapshot", STRUCT_OPS),
    FactSpec("memory.percent", float, SourceEnum.PROCESS, "Memory usage", NUMERIC_OPS),
    FactSpec("memory.info", object, SourceEnum.PROCESS, "Memory info", STRUCT_OPS),
    FactSpec("memory.full_info", object, SourceEnum.PROCESS, "Full memory info", STRUCT_OPS),
    FactSpec("memory.maps", list, SourceEnum.PROCESS, "Memory maps", COLLECTION_OPS),
    FactSpec("io", dict, SourceEnum.PROCESS, "IO statistics", STRUCT_OPS),
    FactSpec("relationships", dict, SourceEnum.PROCESS, "Process relationships", STRUCT_OPS),
    FactSpec("raw", dict, SourceEnum.PROCESS, "Raw snapshot data", STRUCT_OPS),
    FactSpec("extensions", dict, SourceEnum.PROCESS, "Dynamic extensions", STRUCT_OPS),
]
