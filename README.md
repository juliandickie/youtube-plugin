# youtube-plugin

Read YouTube through the official Data API v3, for voice-of-customer research and
channel work. Works on any public channel, routes output per client, and ships both a
CLI and MCP tools over one core.

## Install

```bash
bash scripts/install.sh
```

Creates a venv at `~/.local/share/youtube-plugin/venv`, installs the package with the
MCP extra, and links `youtube` into `~/.local/bin`. Idempotent.

## Set up

1. In Google Cloud Console, on your project (Julian's is `pro-marketing-494311`),
   enable **YouTube Data API v3**
2. APIs and Services, Credentials, create an **API key**
3. Put it in `~/.config/youtube-plugin/config.toml`:

```toml
[youtube]
api_key = "..."

[cache]
enabled = true
ttl_hours = 24
```

No OAuth, no approval process, no consent screen. Public reads need only the key.

Then `youtube doctor`.

### Clients

`~/.config/youtube-plugin/clients.toml` maps a short slug to where that client's
research should land:

```toml
[clients.idd]
name = "Institute of Digital Dentistry"
path = "~/code/idd-world/research/general/source-docs/voc-youtube"
channels = ["@InstituteofDigitalDentistry"]
competitors = ["@SomeCompetitor"]

[clients.acme]
name = "Acme Dental"
path = "~/code/clients/acme/voc"
```

Then `--client idd` writes there. `--out` overrides. Neither means stdout.

## Use

```bash
youtube comments https://youtu.be/E08EG1NiI5k --format voc --client idd
youtube sweep @InstituteofDigitalDentistry --videos 20 --sort discussed --format voc
youtube channel @SomeCompetitor --videos 50
youtube captions <video> --via-yt-dlp
youtube quota
```

## What makes this different from fetching the page

**Replies are resolved in full.** YouTube returns only a subset of replies inline on a
comment thread. This tool notices when a thread's inline replies fall short of its
`totalReplyCount` and fetches the rest. Without that you get a thread that looks
complete and has quietly lost its tail, which is where the long arguments live.

**Search is not implemented, on purpose.** `search.list` is capped at 100 calls a day
in its own quota bucket. Resolving a channel by `@handle` costs 1 unit from the main
10,000. Handles, not search.

**Quota is tracked locally**, keyed by Pacific date because that is when Google resets.
A sweep estimates its cost first and refuses rather than dying halfway with a partial
corpus. The ledger counts this tool's own calls, not Google's view, and says so.

## The voc format

Records shaped for the Ultimate Message Map: verbatim text plus permalink, author,
likes, date, video and depth. The contract matches `reddit-plugin` exactly so corpora
from both merge without transformation.

The language filter defaults to English: `--lang en` is implied on voc output,
`--lang en,de` keeps the languages you name, and `--lang all` keeps everything.
Detection is a stdlib heuristic: script
ranges settle non-Latin languages, stopword scoring handles the rest. Anything under six
words, or any near-tie, returns "unknown" and is **kept**, because dropping on weak
evidence loses real customer lines invisibly. Every drop is audited as `language_<code>`.

**It does not apply the sticky-VOC filter.** That is an eyes-closed human judgement.
The tool removes unambiguous noise only: deleted, bots, under 80 characters,
duplicates, and channel-owner comments. Every drop is counted by reason in an `audit`
block. `--keep-all` disables it.

Text is copied, never rewritten.

## Captions

The official API restricts `captions.download` to videos you have permission to edit,
so there is **no sanctioned route to a third party's transcript**. The official path
also needs OAuth, which arrives in v2.

`--via-yt-dlp` retrieves captions outside the official API. It runs only when
explicitly asked for, never as a fallback, and stamps `"official_api": false` on
everything it returns. That boundary is deliberate and documented in `captions.py`;
please do not "tidy" it into a transparent fallback.

## Roadmap

v2 adds OAuth (reusing the existing Pro Marketing desktop client, kept in Testing
status so no verification is needed) for owned-channel captions, the Analytics API, and
caption upload. Note the Analytics and Reporting APIs are owner-only with no
any-channel mode, so agency use needs each client to authorise.

## Development

```bash
~/.local/share/youtube-plugin/venv/bin/python -m unittest discover -s tests
```

65 tests, no network. Session state and open work in
`SESSION-HANDOFF-2026-09-10.md`. Design record in
`docs/superpowers/specs/2026-09-09-youtube-plugin-design.md`.
