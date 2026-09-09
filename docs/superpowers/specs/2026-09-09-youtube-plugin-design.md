# YouTube Plugin - Design

Date 2026-09-09. Status approved, building.

## Purpose

Read YouTube for voice-of-customer research and channel work, across any channel and
any Pro Marketing client. Scope is deliberately broader than research: owned-channel
captions and analytics are in the roadmap, which is why this is a standalone plugin
rather than a source folded into the reddit VOC tool.

## Research that shaped this

Three lanes of discovery ran on 2026-09-09. Findings that changed the design:

**Nothing adoptable exists.** No first-party YouTube MCP server. Across ~140 listings
only one repo implements real comment pagination, and it carries no licence, so it is
not safely forkable. `kirbah/mcp-youtube` is the best-engineered base but has neither
pagination nor analytics. Build fresh; read others for patterns only.

**Comments are cheap and shallow.** `commentThreads.list` costs 1 unit, needs only an
API key, works on any public video. YouTube caps comment trees at exactly two levels:
"YouTube currently supports replies only for top-level comments." Simpler than Reddit.

**But replies are a subset.** Google's docs state the embedded `replies` list is
partial unless it already equals `snippet.totalReplyCount`. Reading only the embedded
replies silently loses the tail. This is the single most important correctness
requirement in this repo.

**Captions have an ownership ceiling.** `captions.download` costs 200 units and,
verbatim, "requires the user to have permission to edit the video". There is no
official route to a third party's transcript.

**Analytics is owner-only.** Both the Analytics and Reporting APIs are OAuth-only with
no API-key mode and no any-channel mode. Agency use needs per-client consent.

## Decisions

| Decision | Choice | Note |
|---|---|---|
| Surface | CLI **and** MCP over one shared core | Julian's call, overriding a CLI-first recommendation |
| Third-party captions | yt-dlp behind an explicit flag | Julian's call, overriding an official-only recommendation |
| Language | Python, stdlib `urllib` | The official client saves little boilerplate for key-based reads (lane 2 finding), so v1 ships dependency-free. `google-auth` arrives only with OAuth in v2. Service accounts are unsupported by YouTube regardless |
| yt-dlp | Optional, invoked as a subprocess | Never imported. Keeps its version drift out of the core and makes the out-of-API boundary physically visible in the code |
| Search | Not implemented | `search.list` is capped at 100 calls/day in its own bucket. Channels resolve by handle at 1 unit instead |
| Client routing | `clients.toml` mapping names to paths | Julian's call |
| Auth v1 | API key only | Every v1 capability is public data |
| Auth v2 | OAuth reusing the existing Pro Marketing desktop client | Kept in Testing status, which is exempt from sensitive-scope verification |

## The out-of-API boundary

Everything in this tool uses the official API except third-party caption retrieval,
which the API forbids. That path:

- requires an explicit `--via-yt-dlp` flag, never a silent fallback
- is never reached by a retry or an error handler
- stamps `"source": "yt-dlp", "official_api": false` on every record it produces
- is documented as outside the API surface in README, SKILL and `--help`

The reasoning is recorded so a later session does not "tidy" it into a transparent
fallback. A silent fallback would put out-of-API retrieval into results a reader
believes came from the sanctioned path, which is the actual harm.

## Layout

```
youtube_plugin/
  config.py     config.toml, env overrides, API key resolution
  clients.py    clients.toml, name to path resolution
  api.py        Data API transport, quota accounting, pagination
  comments.py   comment threads with full reply resolution
  channels.py   handle/URL/id resolution, uploads-playlist sweep
  captions.py   official (owner) and yt-dlp (flagged) paths
  models.py     normalized Video, Comment, Channel records
  voc.py        UMM shaping, mechanical prefilter, audit
  formats.py    json / markdown / voc
  cli.py        argparse dispatch
  mcp.py        MCP server over the same core
bin/youtube     PATH wrapper
skills/youtube/ thin skill
tests/          fixture-based, no network
```

## Commands

| Command | Quota | Purpose |
|---|---|---|
| `youtube comments <video>` | ~1 per 100 comments | Comments with full reply resolution |
| `youtube channel <handle>` | 1 + 1 per 50 videos | Channel metadata and video list |
| `youtube sweep <handle> --videos N` | ~1 per video plus comment pages | Comments across a channel, own or competitor |
| `youtube captions <video>` | 50 + 200 official | Owned videos; `--via-yt-dlp` for third party |
| `youtube quota` | 0 | Units spent today against 10,000 |
| `youtube clients` | 0 | List configured clients and their paths |
| `youtube doctor` | 0 | Diagnose key, clients.toml, yt-dlp presence |

Global: `--format json|markdown|voc`, `--client <name>`, `--out <path>`, `--limit`,
`--no-cache`.

## VOC output contract

Matches reddit-plugin's `voc` format exactly: same record keys, same `umm` block, same
`audit` accounting, slot legend once per payload. This is deliberate. The methodology
requires triangulating across at least three sources, and that merge is manual work if
each source emits a different shape.

Same two rules as reddit-plugin, for the same reasons:

- **Text is copied verbatim, never rewritten.** Paraphrase destroys sticky VOC.
- **The sticky-VOC filter is NOT implemented and must not be claimed.** Mechanical
  prefilter only, with every drop counted by reason.

## Quota accounting

Every API call increments a per-day counter persisted in the config directory, keyed by
Pacific date since that is when Google resets. `youtube quota` reports it. A sweep that
would exceed the remaining budget warns with an estimate before starting rather than
failing halfway with a partial corpus.

Estimated costs, from Google's quota table: a 200-video channel sweep with 100 comments
each is roughly 204 units. A caption pull is 250 units per video, capping around 40
videos a day, and only on videos you own.

## Testing

Fixture-based, no network. Priority on the reply-subset resolution (the silent-failure
path), quota accounting, `clients.toml` resolution including path traversal refusal,
and the prefilter audit.

## Out of scope for v1

Analytics and Reporting APIs (OAuth, owner-only, needs per-client consent). Caption
upload. Search. Playlist management. Live streaming.
