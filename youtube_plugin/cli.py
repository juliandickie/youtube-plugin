"""Command line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import clients as clients_mod
from . import core, formats
from .api import Api, YouTubeError
from .captions import yt_dlp_available
from .config import CLIENTS_PATH, CONFIG_PATH, ConfigError, Quota
from .config import load as load_config

VERSION = "0.2.0"


def _add_output(parser: argparse.ArgumentParser, *, voc: bool = True) -> None:
    parser.add_argument("--format", choices=formats.FORMATS, default="json")
    parser.add_argument("--client", help="write into this client's path from clients.toml")
    parser.add_argument("--out", help="write to this path (wins over --client)")
    parser.add_argument("--no-cache", action="store_true")
    if voc:
        parser.add_argument("--min-length", type=int, default=None,
                            help="voc: minimum comment length to keep (default 80)")
        parser.add_argument("--keep-all", action="store_true",
                            help="voc: disable the mechanical prefilter")
        parser.add_argument("--lang", default="en",
                            help="voc: keep only these languages, comma separated. "
                                 "Defaults to en; pass 'all' to keep every language. "
                                 "Text too short to classify is always kept, and "
                                 "every drop is audited with the language that was "
                                 "detected.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtube",
        description="Read YouTube for research. Official Data API, plus an explicit "
                    "opt-in yt-dlp path for third-party captions.",
    )
    parser.add_argument("--version", action="version", version=f"youtube-plugin {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("comments", help="comments for one video, replies fully resolved")
    p.add_argument("video", help="video URL or id")
    p.add_argument("--limit", type=int, default=None, help="cap TOP-LEVEL comments")
    p.add_argument("--order", default="relevance", choices=["relevance", "time"])
    p.add_argument("--no-replies", action="store_true")
    _add_output(p)

    p = sub.add_parser("channel", help="channel metadata and video list")
    p.add_argument("channel", help="@handle, channel URL, or UC... id")
    p.add_argument("--videos", type=int, default=0, help="also list this many videos")
    _add_output(p, voc=False)

    p = sub.add_parser("sweep", help="comments across a channel's videos")
    p.add_argument("channel", help="@handle, channel URL, or UC... id")
    p.add_argument("--videos", type=int, default=20)
    p.add_argument("--comments", type=int, default=None, dest="comments_limit",
                   help="cap top-level comments per video")
    p.add_argument("--sort", default="discussed", choices=["recent", "popular", "discussed"],
                   help="which videos to sweep (default discussed, the best for VOC)")
    p.add_argument("--pool", type=int, default=None,
                   help="cap the candidate set that ranking happens over. Default is "
                        "EVERY video on the channel, because ranking only the newest "
                        "page is not ranking. Ignored for --sort recent.")
    p.add_argument("--yes", action="store_true", help="skip the quota confirmation")
    _add_output(p)

    p = sub.add_parser("captions", help="captions for a video")
    p.add_argument("video")
    p.add_argument("--via-yt-dlp", action="store_true", dest="via_yt_dlp",
                   help="OUTSIDE the official API. The API cannot return captions for "
                        "videos you do not have edit permission on.")
    p.add_argument("--lang", default="en", help="comma separated language codes")
    _add_output(p, voc=False)

    sub.add_parser("quota", help="units spent today against the daily limit")
    sub.add_parser("clients", help="list configured clients")
    sub.add_parser("doctor", help="diagnose key, clients.toml, yt-dlp")

    p = sub.add_parser("cache", help="inspect or clear the cache")
    p.add_argument("action", choices=["info", "clear"])

    return parser


def _voc_kwargs(args) -> dict:
    if getattr(args, "format", None) != "voc":
        return {}
    out = {}
    if getattr(args, "min_length", None) is not None:
        out["min_length"] = args.min_length
    if getattr(args, "keep_all", False):
        out["keep_all"] = True
    languages = parse_languages(getattr(args, "lang", None))
    if languages:
        out["languages"] = languages
    return out


def parse_languages(value) -> list[str] | None:
    """Turn a --lang value into a language list, or None for no filtering.

    The default is "en" because every corpus gathered so far wanted it and an
    opt-in flag was forgotten more than once. "all" is the explicit opt-out, so a
    non-English client passes their own codes or "all" rather than relying on an
    absent flag.
    """
    if value is None:
        return None
    codes = [s.strip().lower() for s in str(value).split(",") if s.strip()]
    if not codes or "all" in codes:
        return None
    return codes


def _emit(data, args, filename: str) -> int:
    text = formats.render(data, args.format, **_voc_kwargs(args))
    target = clients_mod.resolve_output(
        getattr(args, "client", None), getattr(args, "out", None), filename
    )
    if target is None:
        print(text)
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(json.dumps({"written": str(target), "bytes": len(text.encode())}, indent=2))
    return 0


def cmd_comments(args, cfg) -> int:
    video, stats = core.video_comments(
        cfg, args.video, limit=args.limit, order=args.order,
        include_replies=not args.no_replies, use_cache=not args.no_cache,
    )
    if stats["threads_needing_reply_fetch"]:
        print(
            f"note: {stats['threads_needing_reply_fetch']} threads had truncated reply "
            f"lists; fetched {stats['replies_fetched']} replies in full.",
            file=sys.stderr,
        )
    ext = "md" if args.format == "markdown" else "json"
    return _emit(video, args, clients_mod.safe_filename("youtube", video.id) + f".{ext}")


def cmd_channel(args, cfg) -> int:
    if args.videos:
        channel, vids = core.channel_videos(
            cfg, args.channel, limit=args.videos, use_cache=not args.no_cache
        )
        payload = {"channel": channel.to_dict(), "videos": [v.to_dict() for v in vids]}
        data = payload if args.format == "json" else vids
    else:
        data = channel = core.channel_info(cfg, args.channel, use_cache=not args.no_cache)
    ext = "md" if args.format == "markdown" else "json"
    name = clients_mod.safe_filename("channel", args.channel.lstrip("@")) + f".{ext}"
    return _emit(data, args, name)


def cmd_sweep(args, cfg) -> int:
    quota = Quota()
    if not args.yes:
        from .channels import plan_sweep

        # Resolve the channel first (1 unit, cached) so the estimate can include the
        # ranking pool. Without its real size the estimate understates badly: on an
        # 806-video channel it read 23 units for a run that cost 77.
        pool_size = args.videos
        if args.sort != "recent":
            try:
                channel = core.channel_info(cfg, args.channel, use_cache=not args.no_cache)
                pool_size = args.pool or channel.video_count or args.videos
            except YouTubeError:
                pool_size = args.pool or args.videos

        estimate = quota.estimate(
            plan_sweep(args.videos, args.comments_limit or 100, pool_size=pool_size)
        )
        remaining = quota.remaining()
        print(
            f"Sweeping up to {args.videos} videos from {args.channel}, "
            f"ranked over {pool_size} candidates.\n"
            f"Estimated floor {estimate} units ({remaining} remaining today). "
            f"Reply fetches are extra and cannot be predicted before fetching.",
            file=sys.stderr,
        )
        if estimate > remaining:
            print(
                "error: that would exceed today's remaining quota. Reduce --videos, "
                "or wait for the midnight Pacific reset.",
                file=sys.stderr,
            )
            return 2

    def progress(i, total, video):
        print(f"[{i}/{total}] {video.title[:70]}", file=sys.stderr)

    channel, vids, totals = core.sweep(
        cfg, args.channel, videos_limit=args.videos, comments_limit=args.comments_limit,
        sort_by=args.sort, pool=args.pool, use_cache=not args.no_cache, on_progress=progress,
    )
    print(json.dumps(totals, indent=2), file=sys.stderr)
    ext = "md" if args.format == "markdown" else "json"
    name = clients_mod.safe_filename("sweep", args.channel.lstrip("@")) + f".{ext}"
    return _emit([v for v in vids if v.comments], args, name)


def cmd_captions(args, cfg) -> int:
    data = core.captions(
        cfg, args.video, via_yt_dlp=args.via_yt_dlp, languages=args.lang.split(","),
    )
    if args.via_yt_dlp:
        print("note: retrieved with yt-dlp, outside the official API.", file=sys.stderr)
    ext = "md" if args.format == "markdown" else "json"
    return _emit(data, args, clients_mod.safe_filename("captions", data["video_id"]) + f".{ext}")


def cmd_quota(args, cfg) -> int:
    print(json.dumps(core.quota_report(cfg), indent=2))
    return 0


def cmd_clients(args, cfg) -> int:
    found = clients_mod.load_all()
    print(json.dumps(
        {"path": str(CLIENTS_PATH), "clients": [c.to_dict() for c in found.values()]},
        indent=2,
    ))
    return 0


def cmd_doctor(args, cfg) -> int:
    try:
        registered = clients_mod.load_all()
        clients_error = None
    except ConfigError as exc:
        registered, clients_error = {}, str(exc)

    report = {
        "version": VERSION,
        "config_path": str(CONFIG_PATH),
        "config_exists": CONFIG_PATH.exists(),
        "api_key_present": bool(cfg.api_key),
        "clients_path": str(CLIENTS_PATH),
        "clients_configured": len(registered),
        "clients_error": clients_error,
        "yt_dlp": yt_dlp_available() or "not installed (only needed for --via-yt-dlp)",
        "quota": core.quota_report(cfg),
        "cache": Api(cfg).cache.info() if cfg.api_key else "unavailable without a key",
    }
    problems = []
    if not cfg.api_key:
        problems.append(
            "No API key. Enable YouTube Data API v3 on your Google Cloud project, "
            f"create a key, and put it in {CONFIG_PATH} under [youtube] as api_key."
        )
    if clients_error:
        problems.append(clients_error)
    report["ok"] = not problems
    report["next_steps"] = problems
    print(json.dumps(report, indent=2, default=str))
    return 0 if not problems else 1


def cmd_cache(args, cfg) -> int:
    cache = Api(cfg).cache
    if args.action == "info":
        print(json.dumps(cache.info(), indent=2))
    else:
        print(json.dumps({"cleared_entries": cache.clear()}, indent=2))
    return 0


HANDLERS = {
    "comments": cmd_comments, "channel": cmd_channel, "sweep": cmd_sweep,
    "captions": cmd_captions, "quota": cmd_quota, "clients": cmd_clients,
    "doctor": cmd_doctor, "cache": cmd_cache,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return HANDLERS[args.command](args, load_config())
    except (ConfigError, YouTubeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
