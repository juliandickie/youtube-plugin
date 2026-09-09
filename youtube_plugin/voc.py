"""VOC shaping for the Ultimate Message Map.

The output contract matches reddit-plugin's `voc` format exactly: same record keys,
same umm block, same audit accounting, slot legend once per payload. That is
deliberate. The methodology requires triangulating across at least three sources, and
that merge becomes manual work the moment two sources emit different shapes.

Two rules carried over unchanged, for the same reasons:

1. Text is copied verbatim, never rewritten. Paraphrasing a captured line is the
   common way strong VOC is destroyed.
2. The sticky-VOC filter is NOT implemented and must not be claimed. It is an
   eyes-closed human judgement about whether a line creates a picture and could not
   have been invented at a writing desk. What runs here is a mechanical prefilter over
   unambiguous noise, and it reports every drop.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import language
from .models import Comment, Video

DEFAULT_MIN_LENGTH = 80

BOT_SUFFIXES = ("bot", "_bot", "-bot")
TOMBSTONES = {"", "[deleted]", "[removed]"}

UMM_SLOTS = [
    "Problems and Motivators",
    "Failed Solutions",
    "Desired Outcome / Dream State",
    "Switching / Habits of the Now",
    "Switching / Worries of the New",
    "Switching / Pushes of the Now",
    "Switching / Pulls of the New",
    "Beliefs and Conversion Precursors",
    "Purchase Criteria",
    "Decision Constraints",
    "Direct Competition - Likes",
    "Direct Competition - Dislikes",
    "All Known Jobs - Functional",
    "All Known Jobs - Personal Emotional",
    "All Known Jobs - Personal Social",
]

NEXT_STEP = (
    "Apply the sticky-VOC filter from voc-research "
    "references/06-filtering-and-processing.md to these records, then tag each keeper "
    "against the Tag Manager and file it into the Ultimate Message Map. Expect roughly "
    "3 to 4 sticky lines per 100 records."
)


@dataclass
class Audit:
    considered: int = 0
    kept: int = 0
    dropped: dict[str, int] = field(default_factory=dict)

    def drop(self, reason: str) -> None:
        self.dropped[reason] = self.dropped.get(reason, 0) + 1

    def to_dict(self) -> dict:
        return {
            "considered": self.considered,
            "kept": self.kept,
            "dropped": dict(sorted(self.dropped.items())),
            "dropped_total": sum(self.dropped.values()),
            "note": (
                "Mechanical prefilter only. The sticky-VOC filter is an eyes-closed "
                "human judgement and has NOT been applied. Re-run with --keep-all to "
                "see every dropped record."
            ),
        }


def _is_bot(author: str | None) -> bool:
    if not author:
        return True
    return author.strip().lower().endswith(BOT_SUFFIXES)


def _drop_reason(
    comment: Comment, min_length: int, seen: set[str], languages: list[str] | None
) -> tuple[str | None, str | None]:
    """Return (drop_reason, detected_language). Language is recorded either way so a
    drop can be audited rather than taken on trust."""
    body = comment.text.strip()
    if body.lower() in TOMBSTONES:
        return "deleted_or_removed", None
    if _is_bot(comment.author):
        return "bot", None
    if comment.is_author:
        return "channel_owner", None  # the brand replying to itself is not customer voice
    if len(body) < min_length:
        return "below_min_length", None
    if body in seen:
        return "duplicate", None
    if languages:
        keep, detected, _ = language.matches(body, languages)
        if not keep:
            return f"language_{detected}", detected
        return None, detected
    return None, None


def shape(
    video: Video,
    *,
    min_length: int = DEFAULT_MIN_LENGTH,
    keep_all: bool = False,
    languages: list[str] | None = None,
) -> dict:
    """One video and its comments to UMM-shaped records plus an audit."""
    audit = Audit()
    seen: set[str] = set()
    records: list[dict] = []
    source_tag = f"YouTube {video.channel_title}" if video.channel_title else "YouTube"

    for comment in video.comments:
        audit.considered += 1
        reason, detected = _drop_reason(comment, min_length, seen, languages)
        if reason and not keep_all:
            audit.drop(reason)
            continue
        seen.add(comment.text.strip())
        audit.kept += 1
        records.append(
            {
                "id": comment.id,
                "text": comment.text,  # verbatim, never modified
                "permalink": comment.permalink,
                "source_tag": source_tag,
                "author": comment.author,
                "score": comment.likes,
                "created": comment.published,
                "depth": comment.depth,
                "is_op": comment.is_author,
                "thread": {
                    "title": video.title,
                    "permalink": video.url,
                    "channel": video.channel_title,
                },
                "language": detected,
                "umm": {"big_picture_tag": None, "granular_tag": None, "slot": None},
                "prefilter": {"kept": True, "reason": reason} if keep_all and reason else {"kept": True},
            }
        )

    return {
        "source": {
            "kind": "youtube_video",
            "title": video.title,
            "permalink": video.url,
            "channel": video.channel_title,
            "views": video.views,
            "comment_count": video.comment_count,
            "created": video.published,
        },
        "records": records,
        "umm_slots": UMM_SLOTS,
        "audit": audit.to_dict(),
        "next_step": NEXT_STEP,
    }


def shape_many(videos: list[Video], **kwargs) -> dict:
    """Combine several videos into one payload with a merged audit."""
    shaped = [shape(v, **kwargs) for v in videos]
    merged = Audit()
    for item in shaped:
        a = item["audit"]
        merged.considered += a["considered"]
        merged.kept += a["kept"]
        for reason, count in a["dropped"].items():
            merged.dropped[reason] = merged.dropped.get(reason, 0) + count
    return {
        "sources": [item["source"] for item in shaped],
        "records": [r for item in shaped for r in item["records"]],
        "umm_slots": UMM_SLOTS,
        "audit": merged.to_dict(),
        "next_step": NEXT_STEP,
    }
