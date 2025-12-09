#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Sequence


CONFIG_PATH_DEFAULT: Final[Path] = Path.home() / ".config" / "ytwrap" / "config.json"


@dataclass(frozen=True)
class AppConfig:
    yt_dlp_binary: str
    download_root: Path
    default_args: tuple[str, ...]


def load_config(config_path: Path) -> AppConfig:
    if not config_path.is_file():
        # Reasonable defaults if the config file is missing.
        download_root = Path.home() / "Downloads" / "ytwrap"
        return AppConfig(
            yt_dlp_binary="yt-dlp",
            download_root=download_root,
            default_args=("--newline",),
        )

    with config_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    yt_dlp_binary = str(raw.get("yt_dlp_binary", "yt-dlp"))
    download_root = Path(raw.get("download_root", str(Path.home() / "Downloads" / "ytwrap")))
    default_args_raw = raw.get("default_args", ["--newline"])

    default_args = tuple(str(arg) for arg in default_args_raw)

    return AppConfig(
        yt_dlp_binary=yt_dlp_binary,
        download_root=download_root,
        default_args=default_args,
    )


def build_target_dir(download_root: Path, subdir: str | None) -> Path:
    if subdir is None or subdir == "":
        return download_root
    return download_root / subdir


def build_command(
    cfg: AppConfig,
    target_dir: Path,
    url: str,
    extra_args: Sequence[str],
) -> list[str]:
    # -P sets the download directory; see `yt-dlp --help`.
    command_parts: list[str] = [
        cfg.yt_dlp_binary,
        "-P",
        str(target_dir),
        *cfg.default_args,
        *extra_args,
        url,
    ]
    return command_parts


def run_command(command: Sequence[str]) -> int:
    completed = subprocess.run(command)
    return int(completed.returncode)


def iter_urls(args: argparse.Namespace) -> Iterable[str]:
    for url in args.urls:
        yield url


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Small wrapper around yt-dlp to download URLs into a fixed directory.",
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more video URLs supported by yt-dlp.",
    )
    parser.add_argument(
        "-C",
        "--config",
        metavar="PATH",
        help=f"Path to config file (default: {CONFIG_PATH_DEFAULT})",
    )
    parser.add_argument(
        "-d",
        "--subdir",
        metavar="NAME",
        help="Optional subdirectory under the download root for this run.",
    )
    parser.add_argument(
        "--extra-arg",
        dest="extra_args",
        action="append",
        default=[],
        help=(
            "Additional yt-dlp argument. "
            "May be passed multiple times, e.g. --extra-arg '-f' --extra-arg 'bestaudio'"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands instead of executing them.",
    )
    return parser.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    config_path = Path(args.config) if args.config is not None else CONFIG_PATH_DEFAULT
    cfg = load_config(config_path)

    target_dir = build_target_dir(cfg.download_root, args.subdir)
    target_dir.mkdir(parents=True, exist_ok=True)

    extra_args = tuple(str(arg) for arg in args.extra_args)

    for url in iter_urls(args):
        command = build_command(cfg, target_dir, url, extra_args)

        if args.dry_run:
            print(" ".join(command))
            continue

        return_code = run_command(command)
        if return_code != 0:
            print(f"yt-dlp exited with status {return_code} for URL: {url}", file=sys.stderr)
            return return_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
