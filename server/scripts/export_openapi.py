from __future__ import annotations

import json
from pathlib import Path

from gateway.main import app


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    output_path = repo_root / "client" / "src" / "generated" / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
