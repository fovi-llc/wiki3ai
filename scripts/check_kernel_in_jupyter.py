"""Ensure the WebLLM lite-kernel federated extension is registered for the Lite site."""

import json
from pathlib import Path


CONFIG_PATH = Path("docs/jupyter-lite.json")
EXT_SCOPE = "@wiki3ai/lite-kernel"
EXT_DIR = Path("docs/extensions") / EXT_SCOPE


def locate_remote_entry() -> str | None:
    static_dir = EXT_DIR / "static"
    if not static_dir.exists():
        return None
    matches = sorted(static_dir.glob("remoteEntry*.js"))
    if not matches:
        return None
    return f"static/{matches[-1].name}"


def main() -> None:
    if not CONFIG_PATH.exists():
        print(f"[build-lite] Warning: jupyter-lite.json not found at {CONFIG_PATH}")
        return

    remote_entry = locate_remote_entry()
    if remote_entry is None:
        print(f"[build-lite] Warning: remoteEntry*.js not found in {EXT_DIR}/static")
        return

    data = json.loads(CONFIG_PATH.read_text())
    config = data.setdefault("jupyter-config-data", {})
    fed_exts = config.setdefault("federated_extensions", [])

    existing = next((ext for ext in fed_exts if ext.get("name") == EXT_SCOPE), None)
    if existing:
        updated = False
        if existing.get("load") != remote_entry:
            existing["load"] = remote_entry
            updated = True
        if existing.get("extension") != "./extension":
            existing["extension"] = "./extension"
            updated = True
        if updated:
            print("[build-lite] Updated lite-kernel entry in jupyter-lite.json")
            CONFIG_PATH.write_text(json.dumps(data, indent=2))
        else:
            print("[build-lite] lite-kernel already present in config")
        return

    print("[build-lite] Injecting lite-kernel into jupyter-lite.json")
    fed_exts.append(
        {
            "name": EXT_SCOPE,
            "extension": "./extension",
            "load": remote_entry,
        }
    )
    CONFIG_PATH.write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
