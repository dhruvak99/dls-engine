from pathlib import Path
import shutil
import json


SOURCE_DIR = Path("data/raw/original_cricsheet_json")
TARGET_DIR = Path("data/raw/cricsheet_json")
TARGET_DIR.mkdir(parents=True, exist_ok=True)

mapping = []

def main():
    files = sorted(SOURCE_DIR.glob("*.json"))

    for idx, src_path in enumerate(files, start=1):
        dst_name = f"match_{idx:04d}.json"
        dst_path = TARGET_DIR / dst_name

        # Copy (not move!)
        shutil.copy2(src_path, dst_path)

        # Optional sanity check: valid JSON
        try:
            with open(dst_path, "r") as f:
                json.load(f)
        except Exception as e:
            print(f"Invalid JSON copied: {dst_name} ({e})")
            dst_path.unlink()
            continue

        mapping.append({
            "original_filename": src_path.name,
            "normalized_filename": dst_name
        })

    # Save mapping for traceability
    with open(TARGET_DIR / "filename_mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"Normalized {len(mapping)} files")


if __name__ == "__main__":
    main()