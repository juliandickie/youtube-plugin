"""Sweep ranking.

Regression guard for a real bug: the first version fetched only the newest 50 videos
and then ranked within them, so on an 806-video channel that posts Shorts daily,
`--sort discussed` returned twenty Shorts with two comments between them while the
genuinely discussed videos sat years back, outside the pool. Ranking a page is not
ranking a channel.
"""

import unittest
from unittest import mock

from youtube_plugin import core
from youtube_plugin.channels import plan_sweep
from youtube_plugin.config import Config
from youtube_plugin.models import Channel, Video


def video(vid, comments, views=0):
    return Video(id=vid, title=f"video {vid}", channel_id="UCx", channel_title="Chan",
                 published="2026-01-01T00:00:00Z", comment_count=comments, views=views)


CHANNEL = Channel(id="UCx", title="Chan", handle="@chan", video_count=806,
                  uploads_playlist="UUx")


class TestRanking(unittest.TestCase):
    def _run(self, sort_by, videos_limit=3, pool=None, catalogue=None):
        catalogue = catalogue or [
            video("new1", 1), video("new2", 0), video("new3", 2),
            video("old_gold", 51), video("old_ok", 20),
        ]
        seen = []

        def fake_channel_videos(config, ref, *, limit=None, hydrate=True, use_cache=True, api=None):
            seen.append(limit)
            return CHANNEL, list(catalogue if limit is None else catalogue[:limit])

        def fake_comments(config, vid, **kwargs):
            v = next(x for x in catalogue if x.id == vid)
            return v, {"replies_fetched": 0, "threads_needing_reply_fetch": 0}

        with mock.patch.object(core, "channel_videos", fake_channel_videos), \
             mock.patch.object(core, "video_comments", fake_comments), \
             mock.patch.object(core, "Api"):
            _, vids, totals = core.sweep(
                Config(api_key="k"), "@chan", videos_limit=videos_limit,
                sort_by=sort_by, pool=pool,
            )
        return vids, totals, seen

    def test_discussed_ranks_the_whole_channel_not_just_the_newest_page(self):
        vids, totals, pools = self._run("discussed")
        self.assertIsNone(pools[0], "pool must be unbounded so ranking spans the channel")
        self.assertEqual(vids[0].id, "old_gold")
        self.assertEqual(totals["candidates_ranked"], 5)

    def test_popular_ranks_by_views(self):
        catalogue = [video("a", 0, views=10), video("b", 99, views=1), video("c", 0, views=500)]
        vids, _, _ = self._run("popular", videos_limit=1, catalogue=catalogue)
        self.assertEqual(vids[0].id, "c")

    def test_recent_needs_no_pool_and_takes_the_newest(self):
        vids, totals, pools = self._run("recent", videos_limit=2)
        self.assertEqual(pools[0], 2, "recent should not fetch a ranking pool")
        self.assertEqual([v.id for v in vids], ["new1", "new2"])

    def test_capped_pool_warns_that_ranking_was_partial(self):
        _, totals, pools = self._run("discussed", pool=2)
        self.assertEqual(pools[0], 2)
        self.assertIn("ranking_note", totals)
        self.assertIn("outside it", totals["ranking_note"])

    def test_unbounded_pool_adds_no_warning(self):
        catalogue = [video(f"v{i}", i) for i in range(806)]
        _, totals, _ = self._run("discussed", catalogue=catalogue)
        self.assertNotIn("ranking_note", totals)

    def test_playlist_shortfall_is_not_blamed_on_pool(self):
        """A channel's video_count and its uploads playlist routinely differ by a few
        (private, removed, members-only). Warning about --pool for that fires a false
        alarm on nearly every run, which is how the real bug presented."""
        catalogue = [video(f"v{i}", i) for i in range(805)]  # channel claims 806
        _, totals, _ = self._run("discussed", catalogue=catalogue)
        self.assertNotIn("ranking_note", totals)

    def test_a_dead_video_does_not_kill_the_sweep(self):
        catalogue = [video("ok1", 5), video("bad", 4), video("ok2", 3)]

        def fake_channel_videos(config, ref, **kwargs):
            return CHANNEL, list(catalogue)

        def fake_comments(config, vid, **kwargs):
            if vid == "bad":
                raise RuntimeError("comments disabled")
            v = next(x for x in catalogue if x.id == vid)
            return v, {"replies_fetched": 0, "threads_needing_reply_fetch": 0}

        with mock.patch.object(core, "channel_videos", fake_channel_videos), \
             mock.patch.object(core, "video_comments", fake_comments), \
             mock.patch.object(core, "Api"):
            _, _, totals = core.sweep(Config(api_key="k"), "@chan", videos_limit=3,
                                      sort_by="discussed")
        self.assertEqual(totals["videos_swept"], 2)
        self.assertEqual(len(totals["skipped"]), 1)
        self.assertEqual(totals["skipped"][0]["video_id"], "bad")


class TestPlan(unittest.TestCase):
    def test_plan_counts_pages_not_videos(self):
        plan = plan_sweep(100, avg_comments=100)
        self.assertEqual(plan["playlistItems.list"], 2)  # 100 videos, 50 per page
        self.assertEqual(plan["commentThreads.list"], 100)

    def test_plan_includes_the_ranking_pool(self):
        """The pool is listed and hydrated even though only `videos` get swept.
        Omitting it understated an 806-video sweep as 23 units when it cost 77."""
        narrow = plan_sweep(20, avg_comments=100)
        wide = plan_sweep(20, avg_comments=100, pool_size=806)
        self.assertEqual(wide["playlistItems.list"], 17)
        self.assertEqual(wide["videos.list"], 17)
        self.assertGreater(sum(wide.values()), sum(narrow.values()))


if __name__ == "__main__":
    unittest.main()
