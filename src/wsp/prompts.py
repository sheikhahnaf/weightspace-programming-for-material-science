"""Build the text an LLM is given for a weight-space programming task.

The harness is model-agnostic: it writes a prompt and reads a reply. Which
model answered, with which tools, is recorded by the experiment, not here.
"""

from __future__ import annotations

from typing import Mapping

import torch

from .serialize import dump_weights

WRITE_REPLY = (
    "Reply with the complete weights in exactly the format shown above: one "
    "'## name shape=(...)' header per tensor, then its rows of numbers. "
    "No other text."
)
EDIT_REPLY = (
    "Reply with a JSON list of edits and no other text. Each edit is "
    '{"tensor": name, "index": [i, ...], "value": number}, with zero-based '
    "indices. Change as few weights as the task needs."
)
READ_REPLY = "Reply in plain prose. Say what you are sure of and what you are guessing."

_REPLY = {"write": WRITE_REPLY, "edit": EDIT_REPLY, "read": READ_REPLY}


def build_prompt(
    mode: str,
    task: str,
    architecture: str,
    state: Mapping[str, torch.Tensor],
    decimals: int = 3,
) -> str:
    """`mode` is 'write' (fill in weights), 'edit' (change some) or 'read' (interpret)."""
    if mode not in _REPLY:
        raise ValueError(f"mode must be one of {sorted(_REPLY)}, not {mode!r}")
    return "\n\n".join(
        [
            "You are given a small neural network as its raw weights. "
            "You cannot run it and you cannot train it.",
            f"# Task\n{task.strip()}",
            f"# Architecture\n{architecture.strip()}",
            f"# Weights\n{dump_weights(state, decimals).strip()}",
            f"# Reply format\n{_REPLY[mode]}",
        ]
    ) + "\n"
