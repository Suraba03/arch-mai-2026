"""
Экспорт OpenAPI-схемы FastAPI в openapi.yaml.

Использование:
    python -m scripts.export_openapi
"""
from pathlib import Path

import yaml

from app.main import app


def main() -> None:
    schema = app.openapi()
    out = Path(__file__).resolve().parent.parent / "openapi.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(schema, f, sort_keys=False, allow_unicode=True)
    print(f"OpenAPI written to {out}")


if __name__ == "__main__":
    main()