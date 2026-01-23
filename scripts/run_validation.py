import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.validator import validate_input
from dls.errors import InputValidationError


def run(relative_path):
    file_path = PROJECT_ROOT / relative_path

    with open(file_path, "r") as f:
        data = json.load(f)

    try:
        validate_input(data)
        print(f"{relative_path}: ✅ VALID")
    except InputValidationError as e:
        print(f"{relative_path}: ❌ INVALID → {e}")


if __name__ == "__main__":
    run("examples/valid_input.json")
    run("examples/invalid_input.json")