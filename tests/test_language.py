"""Language detection and the --lang filter.

The governing rule under test is DO NOT DROP ON WEAK EVIDENCE. Losing a real customer
line to an over-eager filter is worse than keeping a stray foreign one, because the
drop is invisible exactly where it matters.
"""

import unittest

from youtube_plugin import language as L
from youtube_plugin.models import Comment, Video
from youtube_plugin.voc import shape

EN = "I had test driven a Trios to make surgical guides and they were not sitting properly"
DE = "Da ich unter diesem Video viele Kommentare von Leuten gesehen habe die Angst haben"
ES = ("Muchas gracias por el video, es muy util para nosotros los dentistas de verdad "
      "y para todo el equipo de la clinica dental que trabaja con nosotros cada dia")


def comment(text, cid="c1"):
    return Comment(id=cid, author="u", author_channel_id="UCa", text=text, likes=0,
                   published=None, updated=None, depth=0, parent_id=None, video_id="v1")


def video(comments):
    v = Video(id="v1", title="t", channel_id="UCowner", channel_title="Chan", published=None)
    v.comments = comments
    return v


class TestDetect(unittest.TestCase):
    def test_identifies_common_languages(self):
        self.assertEqual(L.detect(EN)[0], "en")
        self.assertEqual(L.detect(DE)[0], "de")
        self.assertEqual(L.detect(ES)[0], "es")

    def test_non_latin_scripts_by_script_alone(self):
        self.assertEqual(L.detect("すばらしいスキャナーですね本当にありがとうございます")[0], "ja")
        self.assertEqual(L.detect("Это отличный сканер спасибо большое за видео")[0], "ru")

    def test_short_text_is_unknown_not_guessed(self):
        for text in ["Great video", "thanks!", "nice one mate"]:
            self.assertEqual(L.detect(text)[0], "unknown", text)

    def test_unknown_is_always_kept(self):
        keep, detected, _ = L.matches("Great video", ["en"])
        self.assertTrue(keep)
        self.assertEqual(detected, "unknown")

    def test_handles_and_urls_do_not_skew_scoring(self):
        noisy = "@somechannel1234 https://example.com/a/b " + EN
        self.assertEqual(L.detect(noisy)[0], "en")

    def test_near_ties_refuse_to_classify(self):
        """English shares function words with its neighbours. A one-word margin is
        not evidence, and guessing there would drop real comments."""
        self.assertEqual(L.detect("de la it is the que")[0], "unknown")

    def test_matches_respects_the_wanted_list(self):
        self.assertTrue(L.matches(EN, ["en"])[0])
        self.assertFalse(L.matches(DE, ["en"])[0])
        self.assertTrue(L.matches(DE, ["en", "de"])[0])


class TestFilterInVoc(unittest.TestCase):
    def test_filters_and_audits_by_detected_language(self):
        out = shape(video([comment(EN, "a"), comment(DE, "b"), comment(ES, "c")]),
                    languages=["en"])
        self.assertEqual(out["audit"]["kept"], 1)
        self.assertEqual(out["audit"]["dropped"]["language_de"], 1)
        self.assertEqual(out["audit"]["dropped"]["language_es"], 1)
        self.assertEqual(out["records"][0]["language"], "en")

    def test_no_lang_means_no_language_filtering(self):
        out = shape(video([comment(EN, "a"), comment(DE, "b")]))
        self.assertEqual(out["audit"]["kept"], 2)
        self.assertIsNone(out["records"][0]["language"])

    def test_every_record_still_accounted_for(self):
        out = shape(video([comment(EN, "a"), comment(DE, "b"), comment(ES, "c")]),
                    languages=["en"])
        a = out["audit"]
        self.assertEqual(a["kept"] + a["dropped_total"], a["considered"])

    def test_keep_all_surfaces_the_language_reason(self):
        out = shape(video([comment(DE, "b")]), languages=["en"], keep_all=True)
        self.assertEqual(out["records"][0]["prefilter"]["reason"], "language_de")
        self.assertEqual(out["records"][0]["language"], "de")


if __name__ == "__main__":
    unittest.main()
