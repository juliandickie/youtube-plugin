# Changelog

## 0.2.0 - 2026-09-11

- The voc language filter now defaults to English on both the CLI and the MCP
  tools. `--lang all` (or `lang="all"`) is the explicit opt-out; a list of codes
  still works. Every corpus so far wanted `en` and the opt-in flag was forgotten more
  than once. `youtube_sweep` on the MCP surface gains `min_length`, `keep_all` and
  `lang`, matching `youtube_comments`.
- The example `clients.toml` uses a fictional agency client rather than a real one.

## 0.1.0 - 2026-09-09

Initial build. Public-data engine, API key only.

- `youtube` CLI plus MCP tools over one shared core (`core.py`), so the surfaces
  cannot drift.
- Comments with **full reply resolution**. YouTube returns the inline `replies` list
  as a subset; threads that fall short of `totalReplyCount` get the remainder fetched
  via `comments.list?parentId`. Without this a thread looks complete and has lost its
  tail.
- Channel resolution by @handle, URL or UC id, and uploads-playlist sweeps that work
  on any public channel including competitors.
- `search.list` deliberately not implemented: it is capped at 100 calls a day in its
  own bucket, while `channels.list` with `forHandle` costs 1 unit from the main pool.
- Local quota ledger keyed by **Pacific date**, because that is when Google resets.
  Sweeps estimate before starting and refuse rather than dying halfway.
- `clients.toml` routing so Pro Marketing client corpora do not mix. Relative paths
  refused; filenames built from channel handles are sanitised against traversal.
- Three formats: `json`, `markdown`, `voc`. The `voc` contract matches reddit-plugin
  exactly so corpora from both merge, which is what triangulation needs.
- Mechanical prefilter with a per-reason audit. The sticky-VOC filter is deliberately
  NOT implemented; it is a human judgement. Channel-owner comments are dropped, since
  the brand replying to itself is not customer voice.
- Captions: official path stubbed pending OAuth in v2 (the API restricts
  `captions.download` to videos you can edit). `--via-yt-dlp` retrieves third-party
  captions outside the API, by explicit request, stamped `official_api: false`, never
  reachable as a fallback.
- v1 core is stdlib only. The MCP SDK is an optional extra; yt-dlp is a subprocess,
  never an import.
- 39 tests, no network. Live-verified: the yt-dlp caption path against a real video.
