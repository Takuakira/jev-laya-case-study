"""Run one repair-cost condition against Laya's typed-decisions model."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import laya


EXPERIMENT_PATH = Path(__file__).with_name("experiment.json")


def replace_placeholders(value: Any, replacements: dict[str, str]) -> Any:
    """Recursively substitute {{name}} placeholders in strings."""
    if isinstance(value, str):
        for key, replacement in replacements.items():
            value = value.replace("{{" + key + "}}", replacement)
        return value
    if isinstance(value, list):
        return [replace_placeholders(item, replacements) for item in value]
    if isinstance(value, dict):
        return {
            key: replace_placeholders(item, replacements)
            for key, item in value.items()
        }
    return value


def build_case(experiment: dict[str, Any], condition_name: str) -> tuple[dict, dict]:
    condition = experiment["conditions"][condition_name]
    state = replace_placeholders(copy.deepcopy(experiment["base_state"]), condition)
    questions = replace_placeholders(copy.deepcopy(experiment["questions"]), condition)
    return state, questions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run one repair-cost condition from experiment.json with Laya."
    )
    parser.add_argument(
        "--condition",
        choices=("10min", "2h", "8h"),
        default="10min",
        help="Repair-cost condition to run (default: 10min).",
    )
    parser.add_argument(
        "--show-input",
        action="store_true",
        help="Print the exact state and questions before inference.",
    )
    args = parser.parse_args()

    experiment = json.loads(EXPERIMENT_PATH.read_text(encoding="utf-8"))
    state, questions = build_case(experiment, args.condition)

    if args.show_input:
        print(json.dumps({"state": state, "questions": questions}, indent=2))

    agent = laya.load(
        "convaiinnovations/laya",
        subfolder="typed-decisions",
    )
    result = agent.predict(state, questions)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

