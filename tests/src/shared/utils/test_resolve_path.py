from dataclasses import dataclass
from typing import Any

import pytest

from shared.utils.resolve_path import resolve_path


@dataclass
class CPU:
    percent: float


@dataclass
class Process:
    cpu: CPU
    pid: int


def test_resolve_path_single_level():
    proc = Process(cpu=CPU(percent=42.5), pid=123)

    assert resolve_path(proc, "pid") == 123


def test_resolve_path_nested():
    proc = Process(cpu=CPU(percent=87.2), pid=456)

    assert resolve_path(proc, "cpu.percent") == 87.2


def test_resolve_path_multiple_nested_levels():
    @dataclass
    class A:
        b: Any

    @dataclass
    class B:
        c: Any

    @dataclass
    class C:
        value: str

    obj = A(b=B(c=C(value="ok")))

    assert resolve_path(obj, "b.c.value") == "ok"


def test_resolve_path_missing_attribute_raises():
    proc = Process(cpu=CPU(percent=10.0), pid=999)

    with pytest.raises(ValueError):
        resolve_path(proc, "cpu.missing")


def test_resolve_path_empty_path_raises():
    proc = Process(cpu=CPU(percent=10.0), pid=999)

    with pytest.raises(ValueError):
        resolve_path(proc, "")