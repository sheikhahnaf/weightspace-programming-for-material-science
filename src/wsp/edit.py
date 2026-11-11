"""Apply an LLM's weight edits to a state dict and report what changed.

An edit names one entry of one tensor and gives its new value:

    [{"tensor": "net.2.bias", "index": [0], "value": -0.4},
     {"tensor": "net.0.weight", "index": [3, 17], "value": 0.0}]

Edits are validated before anything is written, so a bad reply changes nothing.
"""

from __future__ import annotations

import json
import math
from collections import OrderedDict
from dataclasses import dataclass
from typing import Mapping, Sequence

import torch


class EditError(ValueError):
    """An edit cannot be applied to this state dict."""


@dataclass(frozen=True)
class Edit:
    tensor: str
    index: tuple[int, ...]
    value: float


@dataclass(frozen=True)
class DiffReport:
    total: int
    changed: int
    max_abs_change: float
    changed_by_tensor: dict[str, int]

    @property
    def fraction_changed(self) -> float:
        return self.changed / self.total if self.total else 0.0


def parse_edits(text: str) -> list[Edit]:
    """Read edits from a JSON list (the reply format the prompts ask for)."""
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as error:
        raise EditError(f"edits are not valid JSON: {error}") from error
    if not isinstance(raw, list):
        raise EditError("edits must be a JSON list")
    edits = []
    for position, item in enumerate(raw):
        try:
            edits.append(
                Edit(
                    tensor=str(item["tensor"]),
                    index=tuple(int(i) for i in item["index"]),
                    value=float(item["value"]),
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            raise EditError(f"edit {position} is malformed: {item!r}") from error
    return edits


def _check(state: Mapping[str, torch.Tensor], edit: Edit) -> None:
    if edit.tensor not in state:
        raise EditError(f"unknown tensor {edit.tensor!r}")
    shape = tuple(state[edit.tensor].shape)
    if len(edit.index) != len(shape):
        raise EditError(f"{edit.tensor}: index {edit.index} does not match shape {shape}")
    for i, n in zip(edit.index, shape):
        if not 0 <= i < n:
            raise EditError(f"{edit.tensor}: index {edit.index} is outside shape {shape}")
    if not math.isfinite(edit.value):
        raise EditError(f"{edit.tensor}{list(edit.index)}: value is not finite")


def apply_edits(
    state: Mapping[str, torch.Tensor], edits: Sequence[Edit]
) -> "OrderedDict[str, torch.Tensor]":
    """Return a copy of `state` with `edits` applied. The input is not modified."""
    for edit in edits:
        _check(state, edit)
    new_state = OrderedDict((k, v.detach().clone()) for k, v in state.items())
    for edit in edits:
        new_state[edit.tensor][edit.index] = edit.value
    return new_state


def diff(before: Mapping[str, torch.Tensor], after: Mapping[str, torch.Tensor]) -> DiffReport:
    """Count the weights that differ between two state dicts of the same layout."""
    if list(before.keys()) != list(after.keys()):
        raise EditError("state dicts have different tensors")
    total = changed = 0
    largest = 0.0
    by_tensor: dict[str, int] = {}
    for name, old in before.items():
        new = after[name]
        if old.shape != new.shape:
            raise EditError(f"{name}: shape changed from {tuple(old.shape)} to {tuple(new.shape)}")
        delta = (new.to(torch.float64) - old.to(torch.float64)).abs()
        n = int((delta > 0).sum().item())
        total += old.numel()
        changed += n
        if n:
            by_tensor[name] = n
            largest = max(largest, delta.max().item())
    return DiffReport(total=total, changed=changed, max_abs_change=largest, changed_by_tensor=by_tensor)
