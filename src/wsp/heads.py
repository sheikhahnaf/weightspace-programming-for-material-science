"""Small readout heads: the networks this project asks an LLM to read, write and edit.

Sizes are kept inside the range where weight-space programming has been
reported to work from raw weights alone (about 17,000 to 172,000 weights;
see docs/research-runs/2026-11-11-where-wsp-fits.md).
"""

from __future__ import annotations

from typing import Sequence

import torch
from torch import nn


class MLPHead(nn.Module):
    """ReLU multilayer perceptron: in_dim -> hidden... -> out_dim."""

    def __init__(self, in_dim: int, hidden: Sequence[int], out_dim: int = 1):
        super().__init__()
        self.in_dim, self.hidden, self.out_dim = in_dim, tuple(hidden), out_dim
        sizes = [in_dim, *hidden, out_dim]
        layers: list[nn.Module] = []
        for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
            layers.append(nn.Linear(a, b))
            if i < len(sizes) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def describe(self) -> str:
        """The layer formulas, in the words the prompt gives the LLM."""
        sizes = [self.in_dim, *self.hidden, self.out_dim]
        lines = [f"Input x has {self.in_dim} entries. h0 = x."]
        linear_index = 0
        for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
            last = i == len(sizes) - 2
            name = f"net.{linear_index}"
            target = "y" if last else f"h{i + 1}"
            activation = "" if last else "relu"
            body = f"{name}.weight @ h{i} + {name}.bias"
            lines.append(
                f"{target} = {activation + '(' + body + ')' if activation else body}"
                f"   ({name}.weight is {b} x {a}, {name}.bias has {b} entries)"
            )
            linear_index += 1 if last else 2
        return "\n".join(lines)


def zero_(module: nn.Module) -> nn.Module:
    """Set every weight to zero: the starting point for 'write from scratch' tasks."""
    with torch.no_grad():
        for parameter in module.parameters():
            parameter.zero_()
    return module
