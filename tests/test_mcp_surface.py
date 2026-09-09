"""The MCP surface builds and exposes the expected tools.

Worth testing because the SDK renamed FastMCP to MCPServer between majors, and the
failure mode was an ImportError that my own error message misattributed to the SDK
being absent. A build test catches the next rename immediately.

Skips when the optional [mcp] extra is not installed, since the CLI must work without
it.
"""

import asyncio
import unittest

try:
    from youtube_plugin.mcp_server import _server_class, build

    HAVE_SDK = True
except SystemExit:
    HAVE_SDK = False

EXPECTED = {
    "youtube_comments",
    "youtube_channel",
    "youtube_sweep",
    "youtube_captions",
    "youtube_quota",
}


@unittest.skipUnless(HAVE_SDK, "optional [mcp] extra not installed")
class TestMcpSurface(unittest.TestCase):
    def test_server_class_resolves(self):
        self.assertIn(_server_class().__name__, {"MCPServer", "FastMCP"})

    def test_builds_and_registers_every_tool(self):
        tools = asyncio.run(build().list_tools())
        self.assertEqual({t.name for t in tools}, EXPECTED)

    def test_tools_carry_descriptions(self):
        """Descriptions are how Claude picks the right tool, so an empty one is a bug."""
        for tool in asyncio.run(build().list_tools()):
            self.assertTrue((tool.description or "").strip(), f"{tool.name} has no description")

    def test_instructions_warn_about_the_sticky_filter_and_yt_dlp(self):
        """Normalise whitespace first: the source string is hard-wrapped, so a naive
        substring check fails on wording that is actually present."""
        from youtube_plugin.mcp_server import INSTRUCTIONS

        flat = " ".join(INSTRUCTIONS.split()).lower()
        self.assertIn("does not apply the sticky-voc filter", flat)
        self.assertIn("you must not report that it did", flat)
        self.assertIn("outside the official api", flat)


if __name__ == "__main__":
    unittest.main()
