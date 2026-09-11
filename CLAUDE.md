# youtube-plugin - working notes

Read `README.md` for usage,
`docs/superpowers/specs/2026-09-09-youtube-plugin-design.md` for why it is shaped this
way including the three lanes of research behind it, and
`SESSION-HANDOFF-2026-09-11.md` for where the work stopped and what is still open
(it chains back to `SESSION-HANDOFF-2026-09-10.md`, which explains how the tool came to
be shaped).

## Rules specific to this repo

**Never weaken reply resolution.** `comments.py` fetches the remainder of a thread's
replies when the inline list falls short of `totalReplyCount`. That extra call looks
like an optimisation target and is not. Removing it produces threads that look
complete and are missing their tail, and nothing in the output would reveal it. The
tests in `tests/test_comments.py` exist to make that regression loud.

**Never make `--via-yt-dlp` a fallback.** It is reached only by explicit caller
request, never from an except branch or a retry. The reasoning is in the module
docstring of `captions.py`. The harm is not using yt-dlp; it is a reader believing a
transcript came from the sanctioned path when it did not.

**Never let `voc` claim to apply the sticky-VOC filter.** It runs a mechanical
prefilter and says so. A test asserts the wording.

**Never modify captured text.** `voc.py` copies comment bodies verbatim.

**Never rank a sweep over only the newest page.** `core.sweep` fetches EVERY video on
the channel as the candidate set for discussed and popular. This looks like a wasteful
default and is not: the first version capped the pool at 50, so on the 806-video iDD
channel "most discussed" meant "most discussed among this week's Shorts" and returned
20 videos carrying 2 comments between them. Listing and hydrating a whole channel costs
about 34 units against 10,000.

**Do not add `search.list`.** It sits in a 100-call-a-day bucket. Channel resolution
by handle costs 1 unit. Adding search would look convenient and would exhaust in an
afternoon.

**The language filter must never drop on weak evidence.** `language.py` returns
"unknown" (and keeps the record) for anything under six words or any near-tie, because
English shares function words with its neighbours. Losing a real customer line to an
over-eager filter is worse than keeping a stray foreign one, since the drop is invisible
exactly where it matters.

**The language filter defaults to English.** Since 2026-09-11 voc output implies
`--lang en` on both surfaces and `--lang all` is the explicit opt-out. Julian's call:
every corpus so far wanted it and an opt-in flag was forgotten. Keep the two surfaces
in step; `parse_languages` in `cli.py` is the one place the rule lives.

**Keep logic in `core.py`.** The CLI and MCP surfaces are both thin wrappers over it.
Logic added to one surface only will drift.

## Testing

```bash
~/.local/share/youtube-plugin/venv/bin/python -m unittest discover -s tests
```

No network. If a change touches reply resolution, add a case with a more awkward
thread shape first.

## Gotchas

- The quota ledger is keyed by **Pacific** date, not local. Google resets at midnight
  PT and a local-date key would reset at the wrong moment.
- The ledger counts only this tool's calls. Anything else on the same Cloud project
  spends the same 10,000, so Google's number can be higher.
- `captions.list` and the official download path raise until OAuth lands in v2. That
  is intentional, not an unfinished stub to route around.
- `mcp_server.py` is named that way so it does not shadow the installed `mcp` package.
- macOS has no `timeout` command; the yt-dlp subprocess carries its own.
- Comment text uses `textOriginal`, not `textDisplay`, because the latter is
  HTML-escaped and would corrupt verbatim capture.
- A channel's `video_count` and its uploads playlist routinely differ by a few (private,
  removed, members-only). Do not warn about it; that fired a false alarm on every run.
- The sweep pre-flight estimate resolves the channel first so the ranking pool is
  included. Without it an 806-video sweep reported 23 units for a run that cost 77.
- A placeholder API key is truthy. `config.PLACEHOLDERS` treats the shipped
  `PASTE_YOUR_API_KEY_HERE` as absent so `doctor` says what is actually wrong.
