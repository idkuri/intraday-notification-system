from __future__ import annotations

import json
from pathlib import Path

from gateway.main import app

from scripts.export_demo_roster import main as export_demo_roster


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    output_path = repo_root / "client" / "src" / "lib" / "api-client" / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    export_demo_roster()


if __name__ == "__main__":
    main()
