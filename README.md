# Compliance Engine

![Python](https://img.shields.io/badge/Python-3.14-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modular, rules-based process compliance auditing tool written in Python.

The engine monitors running processes,
periodically collects runtime facts,
and evaluates them against a configurable set of compliance rules.
It is designed to be extensible, allowing new rules and data sources
to be added without modifying the core execution pipeline.


## Table of Contents
- [Architecture & Design](#architecture-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Defining Rules](#to-define-new-rules)

## Architecture Overview

The Compliance Engine is structured as a set of loosely coupled components
with clear responsibilities. This separation allows rule logic, data
collection, and execution flow to evolve independently. 
Each evaluation cycle operates over an immutable snapshot to 
ensure deterministic rule outcomes.

### High-Level Flow

1. **Process Attachment**
   - The engine attaches to an existing process (via PID)
        or spawns a new process from a command.
   - Process lifecycle is managed by a dedicated process handler.

2. **Snapshot Collection**
   - At a fixed interval, the engine collects runtime data from 
        the monitored process.
   - Each collection produces a snapshot representing the current state
      of observed facts.

3. **Fact Processing**
   - Raw snapshot data is normalized and registered as facts.
   - Facts are grouped by source and made available to the rules engine
      in a consistent format.

4. **Rule Evaluation**
   - Rules define conditions over one or more facts using typed operators.
   - The rules engine evaluates active rules against the current fact set.
   - Rules may be selectively enabled by name or ID at runtime.

5. **Compliance Reporting**
   - Evaluation results are aggregated and printed to the console.
   - The engine can operate indefinitely or terminate after a configured
      time limit.

### Design Constraints and Non-Goals

- The engine is intentionally single-process to simplify scheduling,
        isolation, and reporting.
- Output is console-based; persistence and alerting are considered
      out of scope.
- Rules are evaluated synchronously to ensure deterministic behavior.


### Extensibility Model

New fact sources and rule types can be added without modifying the core
evaluation loop by registering new sources and rules at startup.

### Error Handling

- Missing or unavailable facts are surfaced explicitly
        during rule evaluation rather than failing implicitly.
- Invalid rules are rejected during loading.
- Process termination is detected and handled gracefully.

### Testing Strategy

Core components are tested in isolation, with end-to-end tests validating
rule evaluation against mocked snapshots.


## Requirements
 - Python 3.14

## Installation
- Clone this repository:

```git clone <repository-url>```
- Navigate to the folder containing the repo with your console.

```cd <repository-folder>```
- Install the dependencies.

```python3 -m pip install .```

## Usage

To monitor a process, you can either attach to an existing PID
or create a new process from a command. Only one process can be
monitored at a time.

```python3 -m src.main {pid} -t {time-limit-in-seconds}```
### Command Line Arguments
To get a list of all available command line arguments:
```python3 -m src.main --help```
```
usage: python3 -m src.main [-h] [-c ...] [-t [TIME_LIMIT]] [-i [INTERVAL]] [-r RULES [RULES ...]] [pid]

positional arguments:
  pid                   Process ID to attach to. If omitted, use -c to create a process.

options:
  -h, --help            show this help message and exit
  -c, --create-process ...
                        Executable and arguments to create a new process.
  -t, --time_limit [TIME_LIMIT]
                        Time limit in seconds. Default to infinity.
  -i, --interval [INTERVAL]
                        Time interval in seconds between test checks. Default is 5.
  -r, --rules RULES [RULES ...]
                        Rule names or ids to test.
```
** Notes:
- Arguments pid and -c are mutually exclusive
- Only one process may be monitored at a time
- Rules may be passed by ID, Name, or a combination of both.

### To Define New Rules
Rules are designed to be composable and extensible,
allowing new compliance logic to be added without modifying the core engine.

Two options are available for defining new rules:

**Option 1**
1. Navigate to project_root/rules/rules.toml
2. Add your rule using the toml format.

Example Rule:
```
[[rules]]
id = "RUL-CPU-MEM-001"
name = "High memory, low CPU"
description = "Trigger when memory usage is high but CPU usage is low"
source = "process"
enabled = true
priority = 10
action = "log"

[rules.model]
operator = "all"
conditions = [
  "cpu.percent < 60",
  "memory.percent > 60",
]
```

**Option 2**
1. Navigate to ```project_root/src/core/rules_engine/builtin_rules/```
2. Create a new Python file or modify an existing one.
3. Use the RuleBuilder to create new rules.
4. Ensure your new rule is imported in the ```__init__.py``` file under ```ALL_BUILTIN_RULES```.

Example:
```
cpu_and_memory_in_bounds = (
    RuleBuilder()
        .define("memory percent and cpu percent 2", "Cpu usage below memory usage above")
        .from_("process")
        .when("cpu.percent < 60")
        .and_("memory.percent > 60")
        .then(lambda: print("Rule 4 Failed"))  # noqa: T201
)
```

## Potential Future Upgrades
**System-Level Monitoring**: Track system metrics in addition to individual
process data.

**Drift Tracking**: Monitor how reported facts evolve between checks.

**Multi-Process Monitoring**: Enable compliance checks for multiple
processes simultaneously.

