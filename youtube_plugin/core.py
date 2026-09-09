"""Operations shared by the CLI and the MCP surface.

Both surfaces call these. Neither reimplements logic, so they cannot drift apart.
Each function returns plain data; rendering and transport belong to the callers.
"""

from __future__ import annotations

from . import captions as captions_mod
from . import channels as channels_mod
from . import comments as comments_mod
from .api import Api, parse_video_id
from .config import Config, Quota
from .models import Video


def _video_with_stats(api: Api, video_id: str, use_cache: bool) -> Video:
    data = api.get(
        "videos.list",
        {"part": "snippet,statistics,contentDetails", "id": video_id},
        use_cache=use_cache,
    )
    items = data.get("items") or []
    if not items:
        from .api import YouTubeError

        raise YouTubeError(f"No video found for {video_id}. Check the id and that it is public.")
    return Video.from_api(items[0])


def video_comments(
    config: Config,
    ref: str,
    *,
    limit: int | None = None,
    order: str = "relevance",
    include_replies: bool = True,
    use_cache: bool = True,
    api: Api | None = None,
) -> tuple[Video, dict]:
    """One video plus its comments with replies fully resolved."""
    api = api or Api(config)
    video_id = parse_video_id(ref)
    video = _video_with_stats(api, video_id, use_cache)
    fetched, stats = comments_mod.fetch(
        api, video_id, limit=limit, order=order,
        include_replies=include_replies, use_cache=use_cache,
    )
    for comment in fetched:
        comment.is_author = bool(
            video.channel_id and comment.author_channel_id == video.channel_id
        )
    video.comments = fetched
    return video, stats


def channel_info(config: Config, ref: str, *, use_cache: bool = True, api: Api | None = None):
    api = api or Api(config)
    return channels_mod.resolve(api, ref, use_cache=use_cache)


def channel_videos(
    config: Config,
    ref: str,
    *,
    limit: int | None = 50,
    hydrate: bool = True,
    use_cache: bool = True,
    api: Api | None = None,
):
    api = api or Api(config)
    channel = channels_mod.resolve(api, ref, use_cache=use_cache)
    vids = channels_mod.videos(api, channel, limit=limit, use_cache=use_cache)
    if hydrate and vids:
        channels_mod.hydrate(api, vids, use_cache=use_cache)
    return channel, vids


def sweep(
    config: Config,
    ref: str,
    *,
    videos_limit: int = 20,
    comments_limit: int | None = None,
    sort_by: str = "recent",
    pool: int | None = None,
    use_cache: bool = True,
    api: Api | None = None,
    on_progress=None,
) -> tuple[object, list[Video], dict]:
    """Comments across a channel's videos. Works on any public channel.

    `sort_by` picks which videos get swept: 'recent', 'popular' by views, or
    'discussed' by comment count. For VOC, 'discussed' is usually right, since a
    video with 400 comments carries more customer voice than a viral one with none.

    `pool` is the CANDIDATE set that ranking happens over, and it matters more than
    it looks. Ranking only the newest page is not ranking: on a channel that posts
    Shorts daily, the most-discussed of the newest 50 is still a pile of Shorts with
    two comments, while the genuinely discussed videos sit years back. So for a
    value-ranked sweep the pool defaults to EVERY video on the channel. That costs
    1 unit per 50 videos to list plus 1 per 50 to hydrate, about 34 units on an
    800-video channel, which is nothing against 10,000. Pass an int to cap it.

    For sort_by='recent' the pool is just videos_limit, because newest-first needs
    no ranking.
    """
    api = api or Api(config)
    quota = api.quota
    pool_limit = videos_limit if sort_by == "recent" else pool
    channel, vids = channel_videos(
        config, ref, limit=pool_limit, hydrate=True, use_cache=use_cache, api=api
    )

    candidates = vids
    if sort_by == "popular":
        vids = sorted(candidates, key=lambda v: v.views or 0, reverse=True)
    elif sort_by == "discussed":
        vids = sorted(candidates, key=lambda v: v.comment_count or 0, reverse=True)
    vids = vids[:videos_limit]

    estimate = quota.estimate(
        channels_mod.plan_sweep(
            len(vids), avg_comments=comments_limit or 100, pool_size=len(candidates)
        )
    )
    totals = {
        "channel": channel.title,
        "channel_video_count": channel.video_count,
        "candidates_ranked": len(candidates),
        "sorted_by": sort_by,
        "videos_swept": 0,
        "comments": 0,
        "replies_fetched": 0,
        "threads_needing_reply_fetch": 0,
        "estimated_floor_units": estimate,
        "skipped": [],
    }
    # Only warn when the caller actually capped the pool. A channel's video_count and
    # its uploads playlist routinely differ by a few (private, removed, or members-only
    # items), and blaming --pool for that would be a false alarm on every run.
    if sort_by != "recent" and pool is not None and len(candidates) >= pool:
        totals["ranking_note"] = (
            f"Ranked {len(candidates)} of {channel.video_count} videos because --pool "
            f"capped the candidate set at {pool}. The true top {videos_limit} may sit "
            f"outside it."
        )

    for index, video in enumerate(vids, start=1):
        if on_progress:
            on_progress(index, len(vids), video)
        try:
            full, stats = video_comments(
                config, video.id, limit=comments_limit,
                use_cache=use_cache, api=api,
            )
        except Exception as exc:  # one dead video must not kill a 200-video sweep
            totals["skipped"].append({"video_id": video.id, "title": video.title, "reason": str(exc)})
            continue
        video.comments = full.comments
        video.views = full.views
        video.comment_count = full.comment_count
        totals["videos_swept"] += 1
        totals["comments"] += len(full.comments)
        totals["replies_fetched"] += stats["replies_fetched"]
        totals["threads_needing_reply_fetch"] += stats["threads_needing_reply_fetch"]

    totals["actual_units_spent_today"] = quota.spent()
    return channel, vids, totals


def captions(config: Config, ref: str, *, via_yt_dlp: bool = False, languages=None) -> dict:
    """Captions for a video.

    The official path needs OAuth and is restricted to videos you can edit, so it
    raises until v2. The yt-dlp path runs ONLY when explicitly asked for, never as a
    fallback from a failure above.
    """
    video_id = parse_video_id(ref)
    if via_yt_dlp:
        return captions_mod.via_yt_dlp(video_id, languages=languages)
    return captions_mod.list_tracks(Api(config), video_id)


def quota_report(config: Config) -> dict:
    return Quota().report()
