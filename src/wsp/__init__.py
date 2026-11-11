"""Harness for weight-space programming experiments on small scientific networks."""

from .edit import DiffReport, Edit, EditError, apply_edits, diff, parse_edits
from .heads import MLPHead, zero_
from .prompts import build_prompt
from .serialize import (
    WeightTextError,
    count_weights,
    dump_weights,
    estimate_tokens,
    load_weights,
    round_trip_error,
)

__all__ = [
    "DiffReport",
    "Edit",
    "EditError",
    "MLPHead",
    "WeightTextError",
    "apply_edits",
    "build_prompt",
    "count_weights",
    "diff",
    "dump_weights",
    "estimate_tokens",
    "load_weights",
    "parse_edits",
    "round_trip_error",
    "zero_",
]
