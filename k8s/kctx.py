#!/usr/bin/env python3
"""
kctx.py — a small, self-contained kubectx-ish helper.

Features
========
- kctx                  → list contexts (marks current, last, and env labels)
- kctx NAME             → switch to context NAME
- kctx -                → toggle to the last context and back
- kctx --current        → print current context
- kctx --rename OLD NEW
- kctx --delete NAME

State is kept in:
    ~/.config/kctx/state.json

Context environment labels (dev/prod/etc.) are configured in:
    ~/.config/kctx/config.toml

Example config.toml:

    [contexts]

    [contexts."ares-dev-shared"]
    env = "dev"

    [contexts."ares-prod-shared"]
    env = "prod"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, List, Dict, Optional

# TOML parsing: prefer stdlib tomllib (3.11+), fall back to tomli if present.
try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:  # pragma: no cover
        tomllib = None  # type: ignore[assignment]

KCTX_DIR: Final[str] = ".config/kctx"
STATE_FILE_NAME: Final[str] = "state.json"
CONFIG_FILE_NAME: Final[str] = "config.toml"

# ANSI color codes (used only when stdout/stderr is a TTY)
ANSI_RESET: Final[str] = "\x1b[0m"
ANSI_RED: Final[str] = "\x1b[31m"
ANSI_GREEN: Final[str] = "\x1b[32m"
ANSI_YELLOW: Final[str] = "\x1b[33m"
ANSI_CYAN: Final[str] = "\x1b[36m"


@dataclass(frozen=True)
class KctxPaths:
    base_dir: Path
    state_file: Path
    config_file: Path


def determine_paths() -> KctxPaths:
    home_dir = Path.home()
    base_dir = home_dir / KCTX_DIR
    state_file = base_dir / STATE_FILE_NAME
    config_file = base_dir / CONFIG_FILE_NAME
    return KctxPaths(base_dir=base_dir, state_file=state_file, config_file=config_file)


def ensure_base_dir(paths: KctxPaths) -> None:
    paths.base_dir.mkdir(parents=True, exist_ok=True)


def run_kubectl(args: List[str]) -> subprocess.CompletedProcess:
    full_args = ["kubectl"] + args
    completed = subprocess.run(
        full_args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed


def get_contexts() -> List[str]:
    completed = run_kubectl(["config", "get-contexts", "-o", "name"])
    if completed.returncode != 0:
        error_message = completed.stderr.strip() or "kubectl failed"
        raise RuntimeError(f"Failed to list contexts: {error_message}")
    lines = [line.strip() for line in completed.stdout.splitlines()]
    contexts = [line for line in lines if line]
    return contexts


def get_current_context() -> Optional[str]:
    completed = run_kubectl(["config", "current-context"])
    if completed.returncode != 0:
        return None
    context_name = completed.stdout.strip()
    if not context_name:
        return None
    return context_name


def use_context(name: str) -> None:
    completed = run_kubectl(["config", "use-context", name])
    if completed.returncode != 0:
        error_message = completed.stderr.strip() or "kubectl failed"
        raise RuntimeError(f"Failed to switch context to {name!r}: {error_message}")


def rename_context(old: str, new: str) -> None:
    completed = run_kubectl(["config", "rename-context", old, new])
    if completed.returncode != 0:
        error_message = completed.stderr.strip() or "kubectl failed"
        raise RuntimeError(
            f"Failed to rename context {old!r} → {new!r}: {error_message}"
        )


def delete_context(name: str) -> None:
    completed = run_kubectl(["config", "delete-context", name])
    if completed.returncode != 0:
        error_message = completed.stderr.strip() or "kubectl failed"
        raise RuntimeError(f"Failed to delete context {name!r}: {error_message}")


def load_state(paths: KctxPaths) -> Dict[str, str]:
    if not paths.state_file.exists():
        return {}
    try:
        raw_text = paths.state_file.read_text(encoding="utf-8")
        state = json.loads(raw_text)
        if not isinstance(state, dict):
            return {}
        state_strings = {str(key): str(value) for key, value in state.items()}
        return state_strings
    except Exception:
        # Corrupt or unreadable state; start fresh.
        return {}


def save_state(paths: KctxPaths, state: Dict[str, str]) -> None:
    ensure_base_dir(paths)
    text = json.dumps(state, indent=2, sort_keys=True)
    paths.state_file.write_text(text, encoding="utf-8")


def record_last_context(paths: KctxPaths, current: Optional[str]) -> None:
    if current is None:
        return
    state = load_state(paths)
    new_state = dict(state)
    new_state["last_context"] = current
    save_state(paths, new_state)


def get_last_context(paths: KctxPaths) -> Optional[str]:
    state = load_state(paths)
    raw_last = state.get("last_context")
    if raw_last is None:
        return None
    return raw_last


def load_labels(paths: KctxPaths) -> Dict[str, str]:
    """
    Load context environment labels from config.toml.

    Expected structure:

        [contexts]

        [contexts."some-context-name"]
        env = "prod"

    Returns:
        Dict[context_name, env_label]
    """
    if tomllib is None:
        return {}
    if not paths.config_file.exists():
        return {}
    try:
        raw_bytes = paths.config_file.read_bytes()
        data = tomllib.loads(raw_bytes.decode("utf-8"))
    except Exception:
        return {}

    contexts_table = data.get("contexts")
    if not isinstance(contexts_table, dict):
        return {}

    labels: Dict[str, str] = {}
    for ctx_name, cfg in contexts_table.items():
        if not isinstance(cfg, dict):
            continue
        env = cfg.get("env")
        if isinstance(env, str):
            labels[str(ctx_name)] = env
    return labels


def format_env_label(env: str, use_color: bool) -> str:
    label = f"[{env}]"
    if not use_color:
        return label
    env_lower = env.lower()
    if env_lower == "prod":
        color = ANSI_RED
    elif env_lower in ("dev", "development"):
        color = ANSI_GREEN
    elif env_lower in ("stage", "staging"):
        color = ANSI_YELLOW
    else:
        color = ANSI_CYAN
    return f"{color}{label}{ANSI_RESET}"


def list_contexts_command(paths: KctxPaths) -> int:
    try:
        contexts = get_contexts()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    current = get_current_context()
    last = get_last_context(paths)
    labels = load_labels(paths)
    use_color = sys.stdout.isatty()

    for name in contexts:
        is_current = name == current
        is_last = (last is not None) and (name == last)
        env = labels.get(name)

        marker_parts: List[str] = []
        if is_current:
            marker_parts.append("●")  # current
        if is_last:
            marker_parts.append("◌")  # last

        marker = " ".join(marker_parts)
        env_label = format_env_label(env, use_color) if env is not None else ""

        pieces: List[str] = []
        if marker:
            pieces.append(f"{marker:3}")
        else:
            pieces.append(" " * 3)
        if env_label:
            pieces.append(f"{env_label:8}")
        pieces.append(name)

        print(" ".join(pieces))

    return 0


def warn_if_prod(context: str, paths: KctxPaths) -> None:
    labels = load_labels(paths)
    env = labels.get(context)
    if env is None:
        return
    if env.lower() == "prod":
        use_color = sys.stderr.isatty()
        env_label = format_env_label(env, use_color)
        print(f"WARNING: context {context!r} is labeled {env_label}", file=sys.stderr)


def switch_context_command(paths: KctxPaths, target: str) -> int:
    # Toggle to last context
    if target == "-":
        current = get_current_context()
        last = get_last_context(paths)
        if last is None:
            print("No last context recorded yet.", file=sys.stderr)
            return 1
        try:
            use_context(last)
        except RuntimeError as error:
            print(str(error), file=sys.stderr)
            return 1
        # For proper toggle behavior, swap last ↔ current.
        if current is not None:
            record_last_context(paths, current)
        new_current = get_current_context()
        if new_current is not None:
            use_color = sys.stdout.isatty()
            labels = load_labels(paths)
            env = labels.get(new_current)
            if env is not None:
                env_label = format_env_label(env, use_color)
                print(f"{env_label} {new_current}")
            else:
                print(new_current)
            warn_if_prod(new_current, paths)
        return 0

    # Normal switch: record current as last, then switch.
    current_before = get_current_context()
    try:
        use_context(target)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    if current_before is not None:
        record_last_context(paths, current_before)

    new_current = get_current_context()
    if new_current is not None:
        use_color = sys.stdout.isatty()
        labels = load_labels(paths)
        env = labels.get(new_current)
        if env is not None:
            env_label = format_env_label(env, use_color)
            print(f"{env_label} {new_current}")
        else:
            print(new_current)
        warn_if_prod(new_current, paths)
    return 0


def current_context_command() -> int:
    current = get_current_context()
    if current is None:
        print("No current context", file=sys.stderr)
        return 1
    print(current)
    return 0


def rename_context_command(old: str, new: str, paths: KctxPaths) -> int:
    try:
        rename_context(old, new)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    # Keep last_context coherent if it referenced the old name.
    state = load_state(paths)
    last = state.get("last_context")
    if last == old:
        new_state = dict(state)
        new_state["last_context"] = new
        save_state(paths, new_state)

    return 0


def delete_context_command(name: str, paths: KctxPaths) -> int:
    state = load_state(paths)
    last = state.get("last_context")
    try:
        delete_context(name)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    if last == name:
        new_state = dict(state)
        new_state.pop("last_context", None)
        save_state(paths, new_state)

    return 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="kctx",
        description="Small helper around 'kubectl config' for managing contexts.",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--current",
        action="store_true",
        help="Print the current context and exit.",
    )
    group.add_argument(
        "--rename",
        nargs=2,
        metavar=("OLD", "NEW"),
        help="Rename a context OLD to NEW.",
    )
    group.add_argument(
        "--delete",
        metavar="NAME",
        help="Delete a context NAME.",
    )

    parser.add_argument(
        "target",
        nargs="?",
        help=(
            "Context to switch to, or '-' to toggle to last context. "
            "If omitted, list contexts."
        ),
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    paths = determine_paths()

    if args.current:
        return current_context_command()

    rename_args = args.rename
    if rename_args is not None:
        old_name, new_name = rename_args
        return rename_context_command(old_name, new_name, paths)

    delete_name = args.delete
    if delete_name is not None:
        return delete_context_command(delete_name, paths)

    target = args.target
    if target is not None:
        return switch_context_command(paths, target)

    return list_contexts_command(paths)


if __name__ == "__main__":
    raise SystemExit(main())
