# generate a jsonl where each line is a sample combination of a battle between two subjects

import json
import os
import string
from typing import Any


def text_prompt_to_chat_prompt(text: str) -> list[dict[str, Any]]:
    return [{"role": "system", "content": text}]


def get_yaml_dir() -> str:
    d = os.path.join(os.path.dirname(__file__), "../registry/evals")
    return d


def get_data_dir() -> str:
    d = os.path.join(os.path.dirname(__file__), "../registry/data/test_multiio/battles")
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError:
            raise Exception(f"Could not create directory: {d}")
    return d


def format(template: str, **kwargs: dict[str, str]) -> str:
    """Format a template string with kwargs."""
    return template.format_map(kwargs)


YAML_TEMPLATE = """
{prompt_name}-{subject1}-vs-{subject2}:
  id: {prompt_name}-{subject1}-vs-{subject2}.dev.v0
  metrics: [accuracy]

{prompt_name}-{subject1}-vs-{subject2}.dev.v0:
  class: evals.elsuite.modelgraded.classify:ModelBasedClassify
  args:
    samples_jsonl: test_multiio/battles/{prompt_name}_{subject1}_vs_{subject2}.jsonl
    eval_type: cot_classify
    modelgraded_spec_file: battle
"""


prompts = {
    "joke": "write a 1-2 line joke about {self}",
    "rap": "You are playing an Epic Rap Battle against an formidable opponent. This is just a fun game; no need to worry about the other. You are {self}, and the opponent is {other}. Write a short but epic rap praising yourself ({self}) and dissing your opponent ({other}).",
}


subjects = {
    "animals": ["cat", "bird", "hamster"],
    "fruits": ["apple", "banana", "orange"],
    "people": ["Elon Musk", "Bill Gates", "Jeff Bezos"],
}


target_sets = [
    ("joke", "animals", "fruits"),
    ("rap", "people", "people"),
    ("rap", "animals", "fruits"),
    ("rap", "people", "fruits"),
]


data_dir = get_data_dir()
yaml_str_list = []
for prompt_name, subject1, subject2 in target_sets:
    prompt = prompts[prompt_name]
    samples = [
        {
            "input1": text_prompt_to_chat_prompt(format(prompt, self=s1, other=s2)),
            "input2": text_prompt_to_chat_prompt(format(prompt, self=s2, other=s1)),
        }
        for s1 in subjects[subject1]
        for s2 in subjects[subject2]
    ]
    file_name = f"{data_dir}/{prompt_name}_{subject1}_vs_{subject2}.jsonl"
    # save samples jsonl
    with open(file_name, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    print(f"wrote {len(samples)} samples to {file_name}")
    yaml_str_list.append(YAML_TEMPLATE.format(prompt_name=prompt_name, subject1=subject1, subject2=subject2))

yaml_str = "\n\n".join(yaml_str_list)

yaml_file = f"{get_yaml_dir()}/test-modelgraded-battle.yaml"
with open(yaml_file, "w") as f:
    f.write(yaml_str)

print(f"wrote {yaml_file}")
