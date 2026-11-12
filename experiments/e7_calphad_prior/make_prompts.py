"""E7: write every prompt that awaits a model reply.

For each Thermo-Calc task, each model and each replicate, two run folders:

  runs/write__<task>__<model>__rep<k>      the E1 write prompt, unchanged
  runs/writepd__<task>__<model>__rep<k>    the same prompt plus binary phase-diagram facts

The prompt text does not depend on the model or the replicate; one folder per
reply keeps each reply with the prompt it answered. The folders are made with
the E1 prompt writer. A prompt that already has a reply is never rewritten
with different text.

    python experiments/e7_calphad_prior/make_prompts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "e1_surrogate_head"))

from llm_arm import write_run  # noqa: E402

from wsp.arms import write_pd_prompt, write_prompt  # noqa: E402
from wsp.tasks import CALPHAD_TASK_NAMES, load_task  # noqa: E402

MODELS = ("opus", "fable")
REPS = (1, 2, 3)
ARMS = {"write": ("write", write_prompt), "write_pd": ("writepd", write_pd_prompt)}


def main() -> None:
    names = []
    for task_name in CALPHAD_TASK_NAMES:
        for arm, (prefix, build) in ARMS.items():
            text = build(load_task(task_name))
            for model in MODELS:
                for rep in REPS:
                    tag = f"{model}__rep{rep}"
                    folder = HERE / "runs" / f"{prefix}__{task_name}__{tag}"
                    if (folder / "reply.txt").exists() and (folder / "prompt.txt").read_text() != text:
                        raise SystemExit(f"{folder.name} has a reply to a different prompt; not overwriting it")
                    names.append(write_run(arm, task_name, HERE / "runs", tag=tag).name)
    print(f"\n{len(names)} runs; awaiting a reply:")
    for name in names:
        if not (HERE / "runs" / name / "reply.txt").exists():
            print(name)


if __name__ == "__main__":
    main()
