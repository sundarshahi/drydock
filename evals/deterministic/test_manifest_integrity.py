"""Guards the publishable manifests (plugin.json, marketplace.json, hooks.json).

WHY THIS MATTERS: These three JSON files are what Claude Code's plugin
marketplace tooling actually parses at install time. A malformed file, a
missing required field, or a version drift between plugin.json and
marketplace.json silently breaks publishing. In particular, `claude plugin
validate --strict` previously failed because marketplace.json was missing a
TOP-LEVEL "description" — this test locks that fix in. It also pins the
version-sync invariant so plugin.json and marketplace.json can never drift
apart unnoticed.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_json(rel: str, failures: list[str]):
    p = ROOT / rel
    if not p.is_file():
        failures.append(f"missing manifest: {rel}")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        failures.append(f"{rel} is not valid JSON: {e}")
        return None


def run() -> list[str]:
    failures: list[str] = []

    # (a) plugin.json
    plugin = _load_json(".claude-plugin/plugin.json", failures)
    plugin_version = None
    if plugin is not None:
        if not isinstance(plugin, dict):
            failures.append("plugin.json: top level must be a JSON object")
        else:
            for field in ("name", "description", "version"):
                val = plugin.get(field)
                if not (isinstance(val, str) and val.strip()):
                    failures.append(f"plugin.json: '{field}' must be a non-empty string")
            if plugin.get("name") != "shipyard":
                failures.append(
                    f"plugin.json: name must be 'shipyard', got {plugin.get('name')!r}"
                )
            plugin_version = plugin.get("version")

    # (b) marketplace.json
    mkt = _load_json(".claude-plugin/marketplace.json", failures)
    mkt_plugin0 = None
    if mkt is not None:
        if not isinstance(mkt, dict):
            failures.append("marketplace.json: top level must be a JSON object")
        else:
            # top-level description (the --strict regression)
            top_desc = mkt.get("description")
            if not (isinstance(top_desc, str) and top_desc.strip()):
                failures.append(
                    "marketplace.json: top-level 'description' must be a non-empty "
                    "string (its absence broke `--strict`)"
                )
            if mkt.get("name") != "shipyard":
                failures.append(
                    f"marketplace.json: name must be 'shipyard', got {mkt.get('name')!r}"
                )
            plugins = mkt.get("plugins")
            if not (isinstance(plugins, list) and plugins):
                failures.append("marketplace.json: 'plugins' must be a non-empty array")
            else:
                mkt_plugin0 = plugins[0]
                if not isinstance(mkt_plugin0, dict):
                    failures.append("marketplace.json: plugins[0] must be an object")
                    mkt_plugin0 = None

    # (e) plugins[0].source and plugins[0].name
    if mkt_plugin0 is not None:
        if mkt_plugin0.get("source") != ".":
            failures.append(
                f"marketplace.json: plugins[0].source must be '.', got "
                f"{mkt_plugin0.get('source')!r}"
            )
        if mkt_plugin0.get("name") != "shipyard":
            failures.append(
                f"marketplace.json: plugins[0].name must be 'shipyard', got "
                f"{mkt_plugin0.get('name')!r}"
            )

    # (c) version sync
    if plugin_version is not None and mkt_plugin0 is not None:
        mkt_version = mkt_plugin0.get("version")
        if plugin_version != mkt_version:
            failures.append(
                f"version drift: plugin.json version {plugin_version!r} != "
                f"marketplace.json plugins[0].version {mkt_version!r}"
            )

    # (d) hooks.json
    hooks = _load_json("hooks/hooks.json", failures)
    if hooks is not None:
        if not isinstance(hooks, dict):
            failures.append("hooks.json: top level must be a JSON object")
        elif not isinstance(hooks.get("hooks"), dict):
            failures.append("hooks.json: top-level 'hooks' must be an object")

    return failures


if __name__ == "__main__":
    import sys

    fails = run()
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        sys.exit(1)
    print(f"PASS: {Path(__file__).name}")
    sys.exit(0)
