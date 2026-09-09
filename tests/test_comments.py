"""Reply resolution. This is the silent-failure path, so it gets the most coverage.

Google returns the embedded `replies` list as a SUBSET when a thread has many
replies. Reading only that subset produces a thread that looks complete and has lost
its tail. These tests exist to make that regression loud.
"""

import unittest

from youtube_plugin import comments as C
from youtube_plugin.models import Comment


def raw_comment(cid, text="a comment", parent=None, video="vid1"):
    snippet = {
        "authorDisplayName": f"user_{cid}",
        "authorChannelId": {"value": f"UC{cid}"},
        "textOriginal": text,
        "likeCount": 3,
        "publishedAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "videoId": video,
    }
    if parent:
        snippet["parentId"] = parent
    return {"id": cid, "snippet": snippet}


def thread(top_id, total_replies, embedded_count):
    return {
        "id": top_id,
        "snippet": {
            "topLevelComment": raw_comment(top_id),
            "totalReplyCount": total_replies,
        },
        "replies": {
            "comments": [raw_comment(f"{top_id}r{i}", parent=top_id) for i in range(embedded_count)]
        } if embedded_count else {},
    }


class FakeApi:
    """Records calls and serves canned reply pages."""

    def __init__(self, threads, reply_pages=None):
        self._threads = threads
        self._reply_pages = reply_pages or {}
        self.calls = []

    def paginate(self, method, params, max_items=None, use_cache=True):
        self.calls.append((method, params.get("parentId") or params.get("videoId")))
        if method == "commentThreads.list":
            items = self._threads[:max_items] if max_items else self._threads
            yield from items
        elif method == "comments.list":
            yield from self._reply_pages.get(params["parentId"], [])


class TestReplySubset(unittest.TestCase):
    def test_detects_a_truncated_reply_list(self):
        self.assertTrue(C.needs_reply_fetch(thread("t1", total_replies=40, embedded_count=5)))

    def test_does_not_refetch_when_already_complete(self):
        self.assertFalse(C.needs_reply_fetch(thread("t1", total_replies=3, embedded_count=3)))

    def test_no_replies_needs_no_fetch(self):
        self.assertFalse(C.needs_reply_fetch(thread("t1", total_replies=0, embedded_count=0)))

    def test_truncated_thread_triggers_a_full_fetch(self):
        t = thread("t1", total_replies=40, embedded_count=5)
        full = [raw_comment(f"t1r{i}", parent="t1") for i in range(40)]
        api = FakeApi([t], {"t1": full})

        result, stats = C.fetch(api, "vid1")

        self.assertEqual(stats["threads_needing_reply_fetch"], 1)
        self.assertEqual(stats["replies_fetched"], 40)
        # 1 top-level + 40 replies, NOT 1 + 5
        self.assertEqual(len(result), 41)
        self.assertIn(("comments.list", "t1"), api.calls)

    def test_fetched_replies_replace_rather_than_append(self):
        """The embedded 5 are a subset OF the 40, so appending would duplicate them."""
        t = thread("t1", total_replies=40, embedded_count=5)
        full = [raw_comment(f"t1r{i}", parent="t1") for i in range(40)]
        result, _ = C.fetch(FakeApi([t], {"t1": full}), "vid1")
        ids = [c.id for c in result]
        self.assertEqual(len(ids), len(set(ids)), "a comment appeared twice")

    def test_complete_thread_makes_no_extra_call(self):
        t = thread("t1", total_replies=2, embedded_count=2)
        api = FakeApi([t])
        result, stats = C.fetch(api, "vid1")
        self.assertEqual(stats["threads_needing_reply_fetch"], 0)
        self.assertEqual(stats["replies_embedded"], 2)
        self.assertEqual(len(result), 3)
        self.assertNotIn("comments.list", [c[0] for c in api.calls])

    def test_include_replies_false_skips_fetching(self):
        t = thread("t1", total_replies=40, embedded_count=5)
        api = FakeApi([t], {"t1": [raw_comment(f"t1r{i}", parent="t1") for i in range(40)]})
        result, stats = C.fetch(api, "vid1", include_replies=False)
        self.assertEqual(stats["replies_fetched"], 0)
        self.assertEqual(len(result), 6)  # top + the 5 embedded


class TestDepthAndShape(unittest.TestCase):
    def test_depth_is_zero_and_one_only(self):
        """YouTube supports no nesting past one level; anything else is a bug."""
        t = thread("t1", total_replies=3, embedded_count=3)
        result, _ = C.fetch(FakeApi([t]), "vid1")
        self.assertEqual(result[0].depth, 0)
        self.assertTrue(all(c.depth == 1 for c in result[1:]))
        self.assertEqual(max(c.depth for c in result), 1)

    def test_replies_inherit_a_parent_id_when_absent(self):
        t = {
            "id": "t1",
            "snippet": {"topLevelComment": raw_comment("t1"), "totalReplyCount": 1},
            "replies": {"comments": [raw_comment("t1r0")]},  # no parentId
        }
        result = C.flatten_thread(t, "vid1")
        self.assertEqual(result[1].parent_id, "t1")

    def test_permalink_points_at_the_comment(self):
        c = Comment(id="abc", author="x", author_channel_id=None, text="t", likes=0,
                    published=None, updated=None, depth=0, parent_id=None, video_id="vid1")
        self.assertEqual(c.permalink, "https://www.youtube.com/watch?v=vid1&lc=abc")

    def test_limit_caps_threads_not_records(self):
        threads = [thread(f"t{i}", total_replies=2, embedded_count=2) for i in range(5)]
        result, stats = C.fetch(FakeApi(threads), "vid1", limit=2)
        self.assertEqual(stats["threads"], 2)
        self.assertEqual(len(result), 6)  # 2 threads x (1 top + 2 replies)
        self.assertTrue(stats["truncated"])

    def test_text_uses_the_original_not_the_html_display_form(self):
        t = {"id": "t1", "snippet": {
            "topLevelComment": {"id": "t1", "snippet": {
                "textOriginal": "raw & unescaped",
                "textDisplay": "raw &amp; unescaped",
                "authorDisplayName": "u", "likeCount": 0, "videoId": "vid1"}},
            "totalReplyCount": 0}}
        result = C.flatten_thread(t, "vid1")
        self.assertEqual(result[0].text, "raw & unescaped")


if __name__ == "__main__":
    unittest.main()
