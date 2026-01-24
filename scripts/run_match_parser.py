from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.match_parser import parse_first_innings


if __name__ == "__main__":
    states = parse_first_innings("data/sample_match.json")

    print("Total states:", len(states))
    print("First 5 states:")
    for s in states[:5]:
        print(s)

    print("\nLast 5 states:")
    for s in states[-5:]:
        print(s)