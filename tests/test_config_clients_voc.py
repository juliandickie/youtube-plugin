"""Quota ledger, client routing, VOC prefilter, and parsing."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from youtube_plugin import clients as clients_mod
from youtube_plugin.api import YouTubeError, parse_channel_ref, parse_video_id
from youtube_plugin.captions import vtt_to_text
from youtube_plugin.config import ConfigError, Quota, load
from youtube_plugin.models import Comment, Video
from youtube_plugin.voc import DEFAULT_MIN_LENGTH, shape

LONG = "The rep quoted me thirty thousand and could not tell me the annual licence cost."
assert len(LONG) >= DEFAULT_MIN_LENGTH


def comment(text=LONG, cid="c1", author="dentist", likes=1, is_author=False):
    return Comment(id=cid, author=author, author_channel_id="UCx", text=text, likes=likes,
                   published="2026-01-01T00:00:00Z", updated=None, depth=0,
                   parent_id=None, video_id="vid1", is_author=is_author)


def video(comments):
    v = Video(id="vid1", title="Scanner review", channel_id="UCowner",
              channel_title="Institute of Digital Dentistry",
              published="2026-01-01T00:00:00Z", comment_count=len(comments))
    v.comments = comments
    return v


class TestQuota(unittest.TestCase):
    def test_charges_documented_costs(self):
        with TemporaryDirectory() as tmp:
            q = Quota(Path(tmp) / "q.json")
            self.assertEqual(q.charge("commentThreads.list"), 1)
            self.assertEqual(q.charge("captions.download"), 200)
            self.assertEqual(q.spent(), 201)
            self.assertEqual(q.remaining(), 10_000 - 201)

    def test_unknown_method_costs_one(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(Quota(Path(tmp) / "q.json").charge("mystery.list"), 1)

    def test_ledger_keeps_only_today(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.json"
            path.write_text('{"1999-01-01": 9999}', encoding="utf-8")
            q = Quota(path)
            self.assertEqual(q.spent(), 0)  # stale day ignored
            q.charge("videos.list")
            self.assertNotIn("1999-01-01", path.read_text())

    def test_corrupt_ledger_does_not_crash(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(Quota(path).spent(), 0)

    def test_estimate_sums_a_plan(self):
        with TemporaryDirectory() as tmp:
            q = Quota(Path(tmp) / "q.json")
            self.assertEqual(
                q.estimate({"commentThreads.list": 10, "captions.download": 1}), 210
            )

    def test_report_admits_it_is_a_local_estimate(self):
        with TemporaryDirectory() as tmp:
            self.assertIn("not read back from Google", Quota(Path(tmp) / "q.json").report()["note"])


class TestClients(unittest.TestCase):
    def _write(self, tmp, body):
        path = Path(tmp) / "clients.toml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_resolves_a_client_path(self):
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, '[clients.idd]\nname = "iDD"\npath = "/tmp/idd"\n')
            self.assertEqual(str(clients_mod.get("idd", path).path), "/tmp/idd")

    def test_relative_paths_are_refused(self):
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, '[clients.x]\npath = "relative/dir"\n')
            with self.assertRaises(ConfigError) as ctx:
                clients_mod.load_all(path)
            self.assertIn("relative path", str(ctx.exception))

    def test_unknown_client_lists_the_known_ones(self):
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, '[clients.idd]\npath = "/tmp/idd"\n')
            with self.assertRaises(ConfigError) as ctx:
                clients_mod.get("nope", path)
            self.assertIn("idd", str(ctx.exception))

    def test_out_beats_client(self):
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, '[clients.idd]\npath = "/tmp/idd"\n')
            got = clients_mod.resolve_output("idd", "/tmp/explicit/file.json", "x.json", path)
            self.assertEqual(str(got), "/tmp/explicit/file.json")

    def test_no_client_and_no_out_means_stdout(self):
        self.assertIsNone(clients_mod.resolve_output(None, None, "x.json"))

    def test_safe_filename_strips_path_traversal(self):
        name = clients_mod.safe_filename("../../etc", "passwd")
        self.assertNotIn("/", name)
        self.assertNotIn("..", name)

    def test_safe_filename_handles_hostile_channel_names(self):
        name = clients_mod.safe_filename("sweep", "@evil/../../../root")
        self.assertNotIn("/", name)
        self.assertTrue(name)


class TestVocPrefilter(unittest.TestCase):
    def test_audit_accounts_for_every_record(self):
        comments = [
            comment(LONG, "keep"),
            comment("nice", "short"),
            comment("[deleted]", "gone"),
            comment(LONG, "dupe"),
            comment(LONG, "bot", author="reviewbot"),
            comment(LONG, "owner", is_author=True),
        ]
        out = shape(video(comments))
        audit = out["audit"]
        self.assertEqual(audit["considered"], 6)
        self.assertEqual(audit["kept"] + audit["dropped_total"], audit["considered"])
        self.assertEqual(audit["kept"], 1)
        for reason in ("below_min_length", "deleted_or_removed", "duplicate", "bot", "channel_owner"):
            self.assertEqual(audit["dropped"][reason], 1, reason)

    def test_text_is_never_modified(self):
        messy = "  spaced   out\n\nand ragged  " + "x" * 90
        self.assertEqual(shape(video([comment(messy)]))["records"][0]["text"], messy)

    def test_never_claims_the_sticky_filter(self):
        self.assertIn("has NOT been applied", shape(video([comment()]))["audit"]["note"])

    def test_slot_legend_is_listed_once(self):
        out = shape(video([comment(LONG + str(i), f"c{i}") for i in range(15)]))
        self.assertIn("umm_slots", out)
        for record in out["records"]:
            self.assertNotIn("candidate_slots", record["umm"])

    def test_contract_matches_reddit_plugin(self):
        """Both tools must emit the same shape or corpora will not merge."""
        record = shape(video([comment()]))["records"][0]
        for key in ("id", "text", "permalink", "source_tag", "author", "score",
                    "created", "depth", "is_op", "thread", "umm", "prefilter"):
            self.assertIn(key, record, f"missing {key}")
        self.assertEqual(set(record["umm"]), {"big_picture_tag", "granular_tag", "slot"})

    def test_keep_all_surfaces_the_reason(self):
        out = shape(video([comment("no", "b")]), keep_all=True)
        self.assertEqual(out["records"][0]["prefilter"]["reason"], "below_min_length")


class TestParsing(unittest.TestCase):
    def test_video_ids(self):
        for value in [
            "https://www.youtube.com/watch?v=E08EG1NiI5k",
            "https://youtu.be/E08EG1NiI5k",
            "https://www.youtube.com/shorts/E08EG1NiI5k",
            "https://www.youtube.com/embed/E08EG1NiI5k",
            "E08EG1NiI5k",
        ]:
            self.assertEqual(parse_video_id(value), "E08EG1NiI5k", value)

    def test_video_id_with_extra_params(self):
        self.assertEqual(
            parse_video_id("https://www.youtube.com/watch?v=E08EG1NiI5k&t=90s&list=PLx"),
            "E08EG1NiI5k",
        )

    def test_bad_video_ref_refused(self):
        with self.assertRaises(YouTubeError):
            parse_video_id("https://example.com/nope")

    def test_channel_refs(self):
        self.assertEqual(parse_channel_ref("@InstituteofDigitalDentistry"),
                         ("handle", "@InstituteofDigitalDentistry"))
        self.assertEqual(
            parse_channel_ref("https://www.youtube.com/channel/UCU0Z-QMwgnNA0J-71SazAfA"),
            ("id", "UCU0Z-QMwgnNA0J-71SazAfA"),
        )
        self.assertEqual(parse_channel_ref("https://www.youtube.com/@somechannel"),
                         ("handle", "@somechannel"))

    def test_bad_channel_ref_refused(self):
        with self.assertRaises(YouTubeError):
            parse_channel_ref("just some words")


class TestVtt(unittest.TestCase):
    def test_strips_timings_tags_and_rolling_repeats(self):
        vtt = (
            "WEBVTT\nKind: captions\nLanguage: en\n\n"
            "00:00:01.000 --> 00:00:03.000\n<c>the scanner</c> was slow\n\n"
            "00:00:03.000 --> 00:00:05.000\nthe scanner was slow\n\n"
            "00:00:05.000 --> 00:00:07.000\nand the software crashed\n"
        )
        self.assertEqual(vtt_to_text(vtt), "the scanner was slow\nand the software crashed")


class TestConfigLoading(unittest.TestCase):
    def test_env_beats_file(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text('[youtube]\napi_key = "from_file"\n', encoding="utf-8")
            with mock.patch.dict("os.environ", {"YOUTUBE_API_KEY": "from_env"}):
                self.assertEqual(load(path).api_key, "from_env")

    def test_missing_key_error_is_actionable(self):
        from youtube_plugin.config import Config

        with self.assertRaises(ConfigError) as ctx:
            Config().require_key()
        self.assertIn("YouTube Data API v3", str(ctx.exception))

    def test_placeholder_key_counts_as_absent(self):
        """The shipped config carries a placeholder. Sending it to Google would
        return an opaque 'API key not valid' instead of saying it was never pasted."""
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text('[youtube]\napi_key = "PASTE_YOUR_API_KEY_HERE"\n', encoding="utf-8")
            with mock.patch.dict("os.environ", {}, clear=True):
                self.assertIsNone(load(path).api_key)

    def test_a_real_looking_key_is_kept(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text('[youtube]\napi_key = "AIzaSyRealLookingKey123"\n', encoding="utf-8")
            with mock.patch.dict("os.environ", {}, clear=True):
                self.assertEqual(load(path).api_key, "AIzaSyRealLookingKey123")


if __name__ == "__main__":
    unittest.main()
