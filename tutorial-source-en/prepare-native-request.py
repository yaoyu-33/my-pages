# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Prepare one typed request offline; no serving, HTTP calls, or model execution."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from nemo_gym.single_agent_turn_types import SingleAgentTurnRequest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--row", type=int, default=0, help="Zero-based JSONL line index")
    parser.add_argument("--taskset", default=None, help="Keep fixed for one run")
    parser.add_argument("--rollout-id", default=None, help="Keep fixed across attempts of one rollout")
    parser.add_argument("--attempt", type=int, default=0)
    args = parser.parse_args()
    if args.row < 0:
        parser.error("--row must be non-negative")
    with args.input.open() as stream:
        row = next((json.loads(line) for i, line in enumerate(stream) if i == args.row), None)
    if row is None:
        parser.error("--row is outside the input file")
    # Routing belongs to the caller/config. Resources receives the task fields.
    excluded = {"responses_create_params", "agent_ref", "task_source", "skills_ref"}
    request = SingleAgentTurnRequest.model_validate({
        "episode_id": {
            "rollout_id": args.rollout_id or f"tutorial-{uuid4().hex}",
            "attempt": args.attempt,
        },
        "task": {
            "task_id": {
                "taskset": args.taskset or f"swebench_pro:tutorial-{uuid4().hex}",
                "task_id": row["instance_id"],
            },
            "task_input": {
                "responses_create_params": row["responses_create_params"],
                "task_data": {
                    key: value for key, value in row.items()
                    if key not in excluded and not key.startswith("_ng_")
                },
            },
        },
    })
    # Refuse to overwrite a previously materialized identity/request.
    with args.output.open("x") as stream:
        stream.write(request.model_dump_json(indent=2) + "\n")
    print(f"Prepared {args.output}; no model call was made")


if __name__ == "__main__":
    main()
