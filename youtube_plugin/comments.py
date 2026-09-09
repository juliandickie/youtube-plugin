"""Comment retrieval with full reply resolution.

THE correctness requirement in this repo. Google's docs on commentThreads.list state
the embedded `replies` list is only a subset unless it already equals
`snippet.totalReplyCount`. Code that reads only the embedded replies returns a thread
that looks complete and has quietly lost the tail, which is exactly where a long
argumentative exchange (the useful VOC) lives.

So: for every thread whose embedded replies fall short of totalReplyCount, fetch the
rest with comments.list?parentId. One extra unit per page, and the ledger records it.

YouTube caps nesting at two levels: "YouTube currently supports replies only for
top-level comments." Depth is therefore 0 or 1, never deeper, and anything claiming
otherwise is a bug.
"""

from __future__ import annotations

from .api import Api
from .models import Comment

THREAD_PARTS = "snippet,replies"
MAX_PAGE = 100


def embedded_replies(thread: dict) -> list[dict]:
    return (thread.get("replies") or {}).get("comments") or []


def total_reply_count(thread: dict) -> int:
    return int((thread.get("snippet") or {}).get("totalReplyCount") or 0)


def needs_reply_fetch(thread: dict) -> bool:
    """True when the embedded replies are a subset and the rest must be fetched."""
    return total_reply_count(thread) > len(embedded_replies(thread))


def flatten_thread(thread: dict, video_id: str | None, extra_replies: list[dict] | None = None) -> list[Comment]:
    """One thread to a flat [top-level, reply, reply, ...] list.

    `extra_replies` replaces the embedded subset when a full fetch was performed,
    rather than being appended, so a comment cannot appear twice.
    """
    out: list[Comment] = []
    top_raw = (thread.get("snippet") or {}).get("topLevelComment")
    if not top_raw:
        return out
    top = Comment.from_snippet(top_raw, depth=0, video_id=video_id)
    out.append(top)

    raw_replies = extra_replies if extra_replies is not None else embedded_replies(thread)
    for raw in raw_replies:
        reply = Comment.from_snippet(raw, depth=1, video_id=video_id)
        if reply.parent_id is None:
            reply.parent_id = top.id
        out.append(reply)
    return out


def fetch(
    api: Api,
    video_id: str,
    *,
    limit: int | None = None,
    order: str = "relevance",
    include_replies: bool = True,
    use_cache: bool = True,
) -> tuple[list[Comment], dict]:
    """All comments for a video. Returns (comments, stats).

    `limit` caps TOP-LEVEL comments, not total records, so a capped pull still
    returns whole threads rather than a thread cut in half.
    """
    comments: list[Comment] = []
    stats = {
        "threads": 0,
        "replies_embedded": 0,
        "replies_fetched": 0,
        "threads_needing_reply_fetch": 0,
        "truncated": False,
    }

    threads = api.paginate(
        "commentThreads.list",
        {
            "part": THREAD_PARTS,
            "videoId": video_id,
            "maxResults": MAX_PAGE,
            "order": order,
            "textFormat": "plainText",
        },
        max_items=limit,
        use_cache=use_cache,
    )

    for thread in threads:
        stats["threads"] += 1
        extra = None
        if include_replies and needs_reply_fetch(thread):
            stats["threads_needing_reply_fetch"] += 1
            top_id = ((thread.get("snippet") or {}).get("topLevelComment") or {}).get("id")
            if top_id:
                extra = list(
                    api.paginate(
                        "comments.list",
                        {"part": "snippet", "parentId": top_id, "maxResults": MAX_PAGE,
                         "textFormat": "plainText"},
                        use_cache=use_cache,
                    )
                )
                stats["replies_fetched"] += len(extra)
        else:
            stats["replies_embedded"] += len(embedded_replies(thread))

        comments.extend(flatten_thread(thread, video_id, extra))

    if limit and stats["threads"] >= limit:
        stats["truncated"] = True
        stats["truncated_note"] = (
            f"Stopped at the --limit of {limit} top-level comments. "
            f"Whole threads were kept; no thread was cut in half."
        )
    return comments, stats
