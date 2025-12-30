"""Built-in rules for process probes."""

from core.rules_engine.rule_builder.rule_builder import RuleBuilder

rule1 = (
    RuleBuilder()
    .define("Cpu Percent", "Cpu usage is above percentage value")
    .from_("process")
    .when("cpu.percent > 60")
    .then(lambda: print("Rule 1 Failed"))  # noqa: T201
)

rule2 = (
    RuleBuilder()
    .define("Cpu Percent", "Cpu usage is below percentage value")
    .from_("process")
    .when("cpu.percent < 60")
    .then(lambda: print("Rule 2 Failed"))  # noqa: T201
)

rule3 = (
    RuleBuilder()
    .define(
        "memory percent and cpu percent",
        "Cpu usage and memory usage are below percentage value",
    )
    .from_("process")
    .when("cpu.percent < 60")
    .and_("memory.percent < 60")
    .then(lambda: print("Rule 3 Failed"))  # noqa: T201
)

rule4 = (
    RuleBuilder()
    .define("memory percent and cpu percent 2", "Cpu usage below memory usage above")
    .from_("process")
    .when("cpu.percent < 60")
    .and_("memory.percent > 60")
    .then(lambda: print("Rule 4 Failed"))  # noqa: T201
)
