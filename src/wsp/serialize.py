"""Turn a network's weights into plain text an LLM can read, and back.

The format follows what the weight-space programming papers report using:
every tensor printed as rounded decimals under a header that names it and
gives its shape (arXiv 2611.08070 rounds to three decimals).

    ## net.0.weight shape=(2, 3)
    0.125 -1.5 0
    0.75 0.031 2
    ## net.0.bias shape=(2,)
    0 -0.5

Tensors with more than two dimensions are printed as rows of their last
dimension; the shape in the header is what restores them.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Mapping

import torch

_HEADER = re.compile(r"^##\s+(\S+)\s+shape=\(([^)]*)\)\s*$")


class WeightTextError(ValueError):
    """The text does not describe a valid set of weights."""


def _format_number(value: float, decimals: int) -> str:
    text = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def dump_weights(state: Mapping[str, torch.Tensor], decimals: int = 3) -> str:
    """Serialise a state dict to text. Rounding is lossy; see `round_trip_error`."""
    lines: list[str] = []
    for name, tensor in state.items():
        tensor = tensor.detach().cpu().to(torch.float64)
        if not torch.isfinite(tensor).all():
            raise WeightTextError(f"{name} contains a non-finite value")
        shape = ", ".join(str(n) for n in tensor.shape)
        if tensor.dim() == 1:
            shape += ","
        lines.append(f"## {name} shape=({shape})")
        rows = tensor.reshape(-1, tensor.shape[-1]) if tensor.dim() > 0 else tensor.reshape(1, 1)
        for row in rows:
            lines.append(" ".join(_format_number(v, decimals) for v in row.tolist()))
    return "\n".join(lines) + "\n"


def load_weights(text: str, dtype: torch.dtype = torch.float32) -> "OrderedDict[str, torch.Tensor]":
    """Parse text written by `dump_weights` (or by an LLM in the same format)."""
    state: "OrderedDict[str, torch.Tensor]" = OrderedDict()
    name: str | None = None
    shape: tuple[int, ...] = ()
    values: list[float] = []

    def close() -> None:
        if name is None:
            return
        expected = 1
        for n in shape:
            expected *= n
        if len(values) != expected:
            raise WeightTextError(
                f"{name}: shape {shape} needs {expected} numbers, found {len(values)}"
            )
        state[name] = torch.tensor(values, dtype=dtype).reshape(shape)

    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        header = _HEADER.match(line)
        if header:
            close()
            name = header.group(1)
            if name in state:
                raise WeightTextError(f"line {line_number}: tensor {name} appears twice")
            try:
                shape = tuple(int(p) for p in header.group(2).split(",") if p.strip())
            except ValueError as error:
                raise WeightTextError(f"line {line_number}: bad shape in header") from error
            values = []
            continue
        if name is None:
            raise WeightTextError(f"line {line_number}: numbers before any '## name shape=(...)' header")
        try:
            row = [float(token) for token in line.replace(",", " ").split()]
        except ValueError as error:
            raise WeightTextError(f"line {line_number}: not a number in {line!r}") from error
        if any(v != v or v in (float("inf"), float("-inf")) for v in row):
            raise WeightTextError(f"line {line_number}: non-finite value")
        values.extend(row)
    close()
    if not state:
        raise WeightTextError("no tensors found")
    return state


def count_weights(state: Mapping[str, torch.Tensor]) -> int:
    return sum(t.numel() for t in state.values())


def round_trip_error(state: Mapping[str, torch.Tensor], decimals: int = 3) -> float:
    """Largest absolute change that printing at `decimals` and reading back makes."""
    restored = load_weights(dump_weights(state, decimals), dtype=torch.float64)
    return max(
        (restored[k] - v.detach().cpu().to(torch.float64)).abs().max().item()
        for k, v in state.items()
    )


def estimate_tokens(text: str) -> int:
    """Rough size of `text` in LLM tokens.

    Digits tokenise poorly, so this uses three characters per token instead of
    the usual four. It is an estimate for budgeting context, not a measurement:
    count with the target model's tokenizer before quoting a number.
    """
    return (len(text) + 2) // 3
