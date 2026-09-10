# Session Handoff - VOC research capability

**Previous handoff:** none. This is the first session of this stream.

## IN FLIGHT - read this first

**`~/code/idd-world` is on another session's branch and was deliberately not touched.**
It sits on `cel26-flight-closeout-2026-08-31` (checked out 2026-08-31) with four
uncommitted files that belong to that stream:

```
M campaigns/2026/2026-08-celebration-sale/CLAUDE.md
M campaigns/2026/2026-08-celebration-sale/ads/CEL26-ASDE-Build-Ledger.md
M campaigns/2026/CLAUDE.md
M log.md
```

This session added `research/voc/` there (7 files, ~520KB: five channel corpora, one
single-video pull, and `ULTIMATE-MESSAGE-MAP.md`). **It is UNTRACKED and uncommitted.**
It was left that way on purpose: committing onto a parallel session's in-flight branch
would entangle the two streams, and switching branches under a live session would be
worse. Julian needs to decide where it lands. Until then it exists only on disk and is
not backed up anywhere.

Everything else this session touched is committed, pushed and clean.

## Goal

Give the `voc-research` methodology the ability to actually reach the sources it names,
then use it. Started from one question: can the voc-research skill scrape Reddit and
other social media, or do connectors need building.

## State

**State verified as of 2026-09-10 11:26 AEST, session 4f083d32-242f-427f-bef1-a096ea7b3f6c**,
by `git status` and `git log`, not from conversation memory.

| Repo | Branch | HEAD | Pushed | Dirty | Notes |
|---|---|---|---|---|---|
| `copy-school` | `voc-capture-paths` | `4c0f295` | yes, 0 unpushed | 3 untracked | Untracked files are a parallel session's 10x-launches audit docs. NOT mine. Merged to main at close, see Landing below |
| `reddit-plugin` | `main` | `4312e2d` | yes, 0 unpushed | clean | PRIVATE github.com/juliandickie/reddit-plugin. Built, tested, BLOCKED externally |
| `youtube-plugin` | `main` | `c6603fd` | yes, 0 unpushed | clean | PRIVATE github.com/juliandickie/youtube-plugin. **WORKING end to end** |
| `idd-world` | `cel26-flight-closeout-2026-08-31` | `98066b9` | n/a | 4 modified + my untracked | **DO NOT TOUCH.** See In Flight above |

**What works right now.** `youtube` CLI is on PATH and live against the Data API with
Julian's key. 458 comment records already gathered across five channels. 440 quota units
spent of 10,000 on 2026-09-09.

**What is blocked.** `reddit` CLI is complete and tested but cannot authenticate:
Reddit's Responsible Builder Policy now gates app creation behind an approval request,
and the create-app form silently reloads instead of erroring. Not fixable in code.

**Not deployed anywhere.** Neither plugin is listed on outfit or loadout.

## Decisions

Chosen, and what was rejected, with reasons. Later decisions supersede earlier options.

| Decision | Chosen | Rejected, and why |
|---|---|---|
| Reddit surface | CLI on PATH plus thin skill | MCP-only: not callable from a shell or another plugin's script, which was the requirement |
| Reddit write access | Present, gated three independent ways | Read-only. **Julian overrode a read-only recommendation.** Gates are token scope, config flag, per-call `--i-am-sure`, deliberately in three files |
| Reddit auth | OAuth refresh token, callback on 8250 | Password grant: puts the Reddit password in plaintext on disk. 8000 is contended by Scribe OAuth |
| YouTube shape | Standalone plugin, CLI **and** MCP | Folding both sources into one `voc` CLI. **Julian overrode this**, wanting scope beyond research (channel management, analytics) |
| YouTube captions | yt-dlp behind an explicit flag | Official-only. **Julian overrode this** after being told the API forbids third-party transcripts |
| YouTube transport | stdlib `urllib` | `google-api-python-client`: saves little boilerplate for API-key reads and adds a dependency tree |
| YouTube search | Not implemented at all | `search.list` sits in a separate bucket capped at 100 calls/day; handle resolution costs 1 unit |
| Ranking pool | Every video on the channel | Newest 50. Ranking a page is not ranking a channel, see Tried and Failed |
| DentalTown brain | **Dropped** | Their terms grant a licence for personal and noncommercial use only and prohibit storing electronically or creating derivative works. iDD is commercial. Not a grey area |
| Apify | Not adopted | Wrong tool for Reddit, where the official API is free and sanctioned. Still the right tool for Instagram and TikTok later |

## Tried and failed

Do not re-attempt these.

- **Reddit MCP connector** (Reddit MCP Buddy): 403 on every call, including the
  subreddits its own error message suggests.
- **Reddit `.json` endpoints**: `www.reddit.com` returns 403; `old.reddit.com` returns
  HTTP **200 with a "Welcome to Reddit" interstitial as the body**. A success code is
  not proof of content.
- **Firecrawl on reddit.com**: refuses the domain by policy, "we do not support this
  site". Search still surfaces Reddit threads; retrieval does not work.
- **In-app browser on reddit.com**: blocked by policy.
- **Creating the Reddit app**: form silently reloads with a link to the Responsible
  Builder Policy. Not a form error, it is the gate.
- **`youtube-comment-downloader`**: recommended by research, rejected on judgement. It
  scrapes, and the official endpoint is 1 quota unit per 100 comments against 10,000/day.

## Julian's feedback this session

- "amh is not my marketplace. We list on outfit and loadout marketplaces and some other
  private marketplaces all owned by juliandickie" - amh is a pointer catalogue to
  Agrici's AI Marketing Hub org repos, not where Julian lists his own work.
- "make sure it works for any YouTube and not just Institute of Digital Dentistry, and
  we can use it across pro marketing clients as well" - drove `clients.toml`.
- "I think I want a standalone plugin that we can have further scope than just
  research" - overrode folding YouTube into the Reddit tool.

## Recipes and footguns

**Working commands**

```bash
youtube doctor
youtube comments <url-or-id> --format voc --limit 20 --client idd
youtube sweep @Handle --videos 20 --sort discussed --format voc --lang en --client idd
youtube quota
~/.local/share/youtube-plugin/venv/bin/python -m unittest discover -s tests   # 65 tests
~/.local/share/reddit-plugin/venv/bin/python -m unittest discover -s tests    # 27 tests
```

**Footguns**

- **zsh does not word-split unquoted expansions.** `for c in "a b"; do cmd $c; done`
  passes ONE argument. Use `${=c}`. This faked 7 of 9 CLI test failures on working code.
- **Bash tool cwd resets between calls.** Use `git -C <path>` or absolute paths. This
  silently ran a test suite in the wrong repo.
- **macOS has no `timeout` command.** Rely on the tool's own subprocess timeout.
- **API key restrictions:** application restriction must be **None**. A referrer
  restriction 403s from a CLI, an IP restriction breaks on network change.
- **Quota ledger is keyed by Pacific date**, because that is when Google resets. It
  counts only this tool's calls, not Google's view of the project.
- **MCP SDK 2.x renamed `FastMCP` to `MCPServer`.** A shim in `mcp_server.py` covers
  both majors. The first error message wrongly blamed the SDK being absent.
- **`captions.download` is owner-only**, so `--via-yt-dlp` is the only route to a third
  party's transcript. It must never become a silent fallback.
- Rebuilding skill zips in `copy-school` re-zips all 20; restore the ones with no
  content change before committing, per that repo's own precedent.

## Open work, ranked

1. **Decide where the iDD VOC corpus lives.** 7 untracked files in
   `idd-world/research/voc/`, currently backed up nowhere.
2. **List both plugins on outfit and loadout**, in lockstep, marketplace.json plus
   README tables in both.
3. **Reddit API approval.** Requires Julian to file the developer or commercial ticket.
   Externally blocked, no code work possible.
4. **Close the VOC research gaps** named in `ULTIMATE-MESSAGE-MAP.md`: Pulls of the New
   is thin, the independence objection is unquantified, Persona B is single-channel, and
   no sales-call VOC exists yet (the top-priority source).
5. **youtube-plugin v2**: OAuth via the existing Pro Marketing desktop client kept in
   Testing status, for owned-channel analytics and captions.
6. **Apify evaluation** for Instagram and TikTok, where no official API exists.

## Questions for Julian

1. Where should `idd-world/research/voc/` land, given idd-world is mid-flight on another
   session's branch? Options: wait for that branch, put it on its own branch off main, or
   move it out of idd-world entirely.
2. Which Reddit API track to file for, developer (non-commercial) or commercial? The app
   description said client brand monitoring, which is the commercial track.
3. Tag both plugins `v0.1.0`? Done at close unless you say otherwise.
4. Should the language filter default to `--lang en` rather than being opt-in?

## Landing

Done as part of this handoff, per the standing session-close authorisation
(commit, push, merge, tag, never deploy). Exact end state recorded in the
"After landing" section appended below.

## After landing

**Verified 2026-09-10 11:31 AEST by `git log` and `git status`.**

| Repo | Branch | HEAD | Tag | Pushed | Dirty |
|---|---|---|---|---|---|
| `copy-school` | `main` | `31dc4ec` (merge commit) | none, repo does not version | yes | 3 untracked, parallel session's, left alone |
| `reddit-plugin` | `main` | `d43258a` | `v0.1.0` | yes, incl. tag | clean |
| `youtube-plugin` | `main` | `82bba9a` | `v0.1.0` | yes, incl. tag | clean |
| `idd-world` | `cel26-flight-closeout-2026-08-31` | `98066b9` | untouched | n/a | **5, see In Flight** |

- `copy-school`: `voc-capture-paths` merged to main with `--no-ff`, then deleted local
  and remote. Lint 0 failures 0 warnings before the merge. The three untracked
  10x-launches audit files were verified unchanged before and after the branch switch.
- Both plugins tagged `v0.1.0`. Neither is listed on a marketplace and **nothing was
  deployed**, which is a separate release decision.
- `idd-world` was not touched. No commit, no branch, no checkout.
