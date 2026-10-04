# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Prepare native Collector inputs; this tutorial helper makes no HTTP calls."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from nemo_gym.episode_types import MaterializedTask, TaskId
from nemo_gym.single_agent_turn_types import SingleAgentTurnTaskInput


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path, help="A new run directory; existing paths are refused")
    parser.add_argument("--limit", type=int, default=1, help="Number of tasks; 0 selects all")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    taskset = f"swebench_pro:{uuid4().hex}"
    tasks = []
    seen = set()
    with args.input.open() as source:
        for line in source:
            row = json.loads(line)
            task = MaterializedTask[SingleAgentTurnTaskInput](
                task_id=TaskId(taskset=taskset, task_id=row["instance_id"]),
                task_input=SingleAgentTurnTaskInput(
                    responses_create_params=row["responses_create_params"],
                    task_data={
                        k: v for k, v in row.items()
                        if k not in {"responses_create_params", "agent_ref", "task_source", "skills_ref"}
                        and not k.startswith("_ng_")
                    },
                ),
            )
            if task.task_id.task_id in seen:
                raise ValueError(f"Duplicate instance_id: {task.task_id.task_id}")
            seen.add(task.task_id.task_id)
            tasks.append(task.model_dump(mode="json", exclude_unset=True))
            if args.limit and len(tasks) >= args.limit:
                break
    if not tasks:
        raise ValueError("Input contains no tasks")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    with (args.output_dir / "tasks.jsonl").open("x") as output:
        for task in tasks:
            output.write(json.dumps(task) + "\n")
    # JSON is valid YAML; quoting the run-unique taskset avoids YAML key ambiguity.
    with (args.output_dir / "routing.yaml").open("x") as output:
        json.dump({
            "environment_routing_mode": "taskset",
            "environment_server_routes": {taskset: "single_agent_turn"},
        }, output, indent=2)
        output.write("\n")
    print(f"Prepared {len(tasks)} task(s) in {args.output_dir}; taskset={taskset}")


if __name__ == "__main__":
    main()
