# Apify for Instagram and TikTok VOC - evaluation

Drafted 2026-09-11. Open item 5 from `SESSION-HANDOFF-2026-09-11.md`. The question is
whether Apify is the right way to add Instagram and TikTok comments to the voice-of-customer
corpus that the `youtube` CLI already feeds, and if so what it costs, what it risks, and what
shape the tool should take. This is an evaluation, not a build. Nothing was run on Apify.

Everything marked VERIFIED below was read from the live page or tool on 2026-09-11 in this
session. Everything marked REPORTED came from a research agent's report and carries the URL
it cited. Nothing here is from memory.

## The short version

- Instagram is the source worth having. All five brands have audiences of 33,000 to 87,000
  followers there. TikTok is not: two competitors are dormant and one is private.
- The official Instagram API returns full comment threads on iDD's own posts and nothing
  but counts on anyone else's, at any access tier. So iDD's own comments should come the
  official way, and competitor comments can only come by scraping or by hand.
- An Apify account already exists (welcomed 2026-06-04, julian@promarketing.co, Free plan,
  USD 5 credit unused this cycle) and a working API token sits in the Pro Marketing
  1Password vault as "API Apify", created 2026-09-09. Firecrawl refuses both platforms by
  policy. Nothing else in the stack reaches them.
- Apify's logged-out actors would do the 20,000-comment competitor sweep for about USD 10
  of actor spend plus a USD 19 Starter month. TikTok would add under USD 5 for the two
  accounts with any audience.
- Meta's and TikTok's written terms prohibit it, US case law says logged-out public scraping
  breaches neither contract nor the CFAA, no enforcement against buyers of scraped data was
  found, and the voc-research skill's own conduct rule says not to bulk-extract around a
  block. That rule collision is the real decision, and it is Julian's.
- Recommendation: do the official route for iDD's own comments now; decide the policy
  question before building anything for competitors; treat TikTok as a rider, not a project.

## What already exists on this machine and in Julian's accounts

Checked before evaluating anything new, per the reuse-before-build rule.

| Thing | State | How verified |
|---|---|---|
| Apify account | EXISTS. Welcome email from Apify dated 2026-06-04, addressed to julian@promarketing.co, in the Pro Marketing inbox; the console login is GitHub OAuth (1Password item "Apify", Pro Marketing account, Personal vault). Username on Apify is juliandickie. FREE plan, USD 5 credit a month, usage this cycle (2026-09-04 to 2026-10-03) effectively zero. | Gmail search via scribe, 1Password, and a live read of `/v2/users/me` and `/v2/users/me/limits`, VERIFIED |
| Apify API token | EXISTS in 1Password: item "API Apify", Pro Marketing account, Personal vault, bearer, created 2026-09-09, valid to 2027-09-01. Nothing on disk (`~/.config` has no apify entry, no env var, nothing in the Claude config), which is the right state; a build would read it via `op://Personal/API Apify/credential` the way the ClickUp plugin does. The token was verified live against the account endpoint in this session without being written anywhere. | 1Password CLI and a live API read, VERIFIED |
| Apify connector in the claude.ai MCP registry | None. The registry returns TikTok Shop, vidIQ, Supermetrics and ad-platform connectors for those keywords, nothing from Apify. | mcp-registry search, VERIFIED |
| Firecrawl on instagram.com and tiktok.com | REFUSED by policy on both, same wording as reddit.com: "we do not support this site". Not a rate limit, not a render failure. | firecrawl_scrape on one post per platform, VERIFIED |
| WebFetch on tiktok.com | Returns a "Please wait..." bot-challenge shell, no content. | VERIFIED on four profile URLs |
| In-app browser on tiktok.com | Loads profiles after a five-second wait. Follower counts, bios and video grids render logged out. | VERIFIED on five profiles |
| In-app browser on instagram.com | Profile header renders logged out (followers, bio, pinned highlights). A post page renders the caption and like count but no comments; the comment area is a "Sign up / Log In" wall. | VERIFIED on one profile and one post |
| iDD Instagram on the Meta connection | The Pipeboard Meta Ads connection lists iDD's Instagram business account (username idigitaldentistry, about 33,000 followers) as linked to the iDD ad account. Reading its posts fails with Meta error code 10, "Application does not have permission for this action". Pipeboard's own hint: the connection predates their 2026-05-04 instagram_basic approval and needs a reconnect at pipeboard.co/connections to pick up the scope. | get_instagram_accounts and get_instagram_posts, VERIFIED |
| Official Meta Ads MCP (mcp.facebook.com) | Connected. Has ads_get_ig_accounts and ads_get_ig_media, which list boostable media. No comment-reading tool on either Meta MCP. | Tool list, VERIFIED |

## The five accounts, sized

Follower counts read from the live profile pages in the in-app browser on 2026-09-11, or
from the search snippet where noted. The YouTube corpus used the same five brands.

| Brand | Instagram | TikTok |
|---|---|---|
| iDD | idigitaldentistry, about 33,000 followers (from the Meta connection) | idigitaldentistry, 1,239 followers, 4,495 likes, VERIFIED |
| 3Shape | 3shape, 86,500 followers, VERIFIED | 3shapedental, 1,676 followers, 17,600 likes, bio "3Shape A/S Official Account", VERIFIED |
| iTero (Align) | iteroscanner, about 42,000 followers (search snippet) | iteroscanner is a PRIVATE account with 0 followers, 0 videos, no bio, VERIFIED. No usable corporate presence. |
| Medit | meditcompany, about 34,000 followers (search snippet) | meditcompany, 22 followers, 9 likes, VERIFIED. Dormant. |
| Dentsply Sirona | dentsplysirona, about 82,000 followers (search snippet); many regional accounts including dentsplysironaanz | dentsplysirona (display name "Digital Dentistry"), 223 followers, 1 like, VERIFIED. Dormant. |

What this means before any pricing is read:

- **Instagram is the real source.** All five brands have audiences in the tens of thousands.
  Comment volume per post is unknown until something reads it, because logged-out Instagram
  withholds comments.
- **TikTok is thin for this market.** Two of the four competitors are dormant and one is
  private. A "20 most-discussed videos per brand" sweep is only meaningful for 3Shape and iDD.
  Whatever TikTok costs, the yield ceiling is low, and the methodology's own warning applies:
  do not reach for a source because it is scrapeable rather than because it is high on the
  priority order.
- **Neither platform moves up the source priority.** Both sit with YouTube at the sixth tier
  in `references/01-system.md` of the voc-research skill. Sales-call VOC (tier one) is still
  unmined. This evaluation does not change that ranking; it only answers whether the door is
  open and what it costs to walk through.

## Instagram via Apify

REPORTED by the Instagram research agent, read 2026-09-11. The four prices the recommendation
rests on were re-read from the live Store pages in the main session and matched (marked
SPOT-CHECKED).

**Platform plans** (apify.com/pricing, SPOT-CHECKED). Free USD 0 with USD 5 credit a month,
Starter USD 19 with USD 19 credit, Scale USD 199, Business USD 999. Pay-per-event actors draw
on that credit: "Both models draw on the platform usage credits included in your plan, and
excess usage is charged to your next invoice." Residential proxy USD 8 per GB, not needed for
the actors below (they carry their own).

**The account is on the Free plan**, confirmed by a live read of the account endpoint: plan
FREE, USD 5 credit a month, current cycle usage a fraction of a cent. No invoice or receipt
from Apify exists in either inbox. A one-account pilot on scrapesmith (20 posts x 200
comments = 4,000 comments = USD 2) fits inside the free credit; the full five-account sweep
does not.

**Actors.** All run logged out and take no cookies unless noted. Prices are per comment on
the Free tier where tiered.

| Actor | Price | Replies | Cap per post | Scale and health |
|---|---|---|---|---|
| apify/instagram-comment-scraper (official) | from USD 1.90 per 1,000 (Free tier USD 0.0026 per comment, Diamond USD 0.0014) | Only on a paid plan: "This feature is for paying users only. If checked, the scraper will extract replies for each comment." SPOT-CHECKED | None stated; "delivers as many comments and replies as it can access" | 53,000 users, 9.9 million runs, 100% stated success, 4.66 from 67 reviews. SPOT-CHECKED |
| apify/instagram-scraper (official, general) | Free tier USD 0.0027 per result | Paid plans only | Free plan: "only the top 15 comments sorted by newest" | 390,000 users, 192 million runs |
| apify/instagram-post-scraper (official) | Free tier USD 0.0017 per post | Preview only | "first and latest comments" only, not a comment tool | 127,000 users |
| apify/instagram-reel-scraper (official) | Free tier USD 0.0026 per reel, plus per-event extras | Preview only | "up to 10 latest comments"; the page itself points to the comment scraper for the rest | 143,000 users |
| scrapesmith/instagram-comments-scraper | USD 0.50 per 1,000, flat, plus USD 0.00005 per run. SPOT-CHECKED. **Refuses Free-plan accounts**: README, "free accounts are limited to 0 results per run on this Actor. Upgrade to a paid plan"; confirmed by the 2026-09-12 pilot run log, "FREE USER detected: hard capped at 0". Missed on 2026-09-11. | Yes, nested `replies` array and `repliesCount`. SPOT-CHECKED | `maxCommentsPerPost`, no hard cap | 2,000 users, 90,000 runs, 100% stated success, 4.41 from 18 reviews, created 2025-10-31 |
| supreme_coder/instagram-comments-scraper | Free tier USD 0.001 per comment, USD 0.0003 on any paid tier | Yes, `scrapeReplies` with thread depth | `limitPerSource` | 529 users, 3.63 from 4 reviews, created 2026-06-24 |
| api-empire/instagram-comments-scraper | not checked | not checked | not checked | Needs a `sessionId` cookie from your own Instagram account. Disqualified on that alone: it puts an iDD login into the scrape. |

Output on the official actor: comment id, post id, text, position, timestamp, owner id and
username and verification, replies, like count, comment url. On scrapesmith: postId, postUrl,
commentId, text, timestamp, likesCount, userId, username, userFullName, isVerified,
repliesCount, replies. Both cover the voc record shape.

**The official actor's own scope note matters.** "The scraper extracts only the comments shown
to Instagram users who are not logged in." That is both the reason it is safe to run without
an iDD credential and the reason its yield may fall short of what a signed-in reader sees.

**Worked cost, 5 accounts x 20 posts x 200 comments = 20,000 comments.**

| Path | Comments | Plan | Total |
|---|---|---|---|
| scrapesmith on Free | 20,000 x 0.0005 = USD 10.00 | Exceeds the USD 5 Free credit, so one month of Starter (USD 19) or a top-up | about USD 19 to 29 for the month, of which USD 10 is the sweep |
| Official actor, replies on | needs a paid plan; Starter tier price is not published separately, Free tier is USD 0.0026 so 20,000 = USD 52 as a ceiling, Diamond USD 28 as a floor | Starter | USD 19 plus roughly USD 40 to 50 |

Pay-per-event bills only comments returned, so these are ceilings. Smaller competitor posts
will cost less.

**Ranking "most discussed" on Instagram.** The official post scraper and the general scraper
both return `commentsCount` per post, so the same client-side pattern as TikTok applies:
list 100 to 200 posts per profile, sort locally, take 20, pass URLs to the comments actor.

**Apify's stated position.** Their blog: "Web scraping is legal if you scrape data that is
publicly available on the internet", with the disclaimer "We are lawyers, but we are not your
lawyers." Their Acceptable Use Policy does not name Instagram. Their General Terms put the
weight on the customer: "You are solely responsible for the legality, accuracy, quality,
appropriateness, and use of all Customer Data", plus an indemnity to Apify for third-party
claims arising from use of any Actor. A community question on the official actor asking
"Does it comply with Instagram's terms and conditions?" exists; the agent could not retrieve
the maintainer's answer (UNVERIFIED).

**Caution on sources.** use-apify.com looks like Apify documentation and is not. It is an
affiliate site that states it is "not owned, operated, or endorsed by Apify Technologies
s.r.o." Nothing above is taken from it.

## TikTok via Apify, and TikTok's official APIs

REPORTED by the TikTok research agent, read 2026-09-11.

**No official TikTok API is open to this team.** Four products exist and none fits:

| API | Returns comments | Whose videos | Open to a commercial AU company |
|---|---|---|---|
| Research API | Yes, with PII redacted | Any, if eligible | No. Eligibility is "academic institutions in the U.S., EEA, UK, Canada, or Switzerland; or not-for-profit... in the EU", and applicants must be "independent of commercial interests". The FAQ answers "I am a creator, advertiser, or commercial user. Am I eligible?" with "No." (developers.tiktok.com/products/research-api, developers.tiktok.com/doc/research-api-faq) |
| Display API | No, metadata only | Own, after OAuth | Not useful, no comment endpoint |
| Content Posting API | No, publish only | Own | Not relevant |
| Commercial Content API | No, ad transparency only | n/a | Not relevant |

**Apify actors.** All run logged out, none need cookies. Prices are the list rate on the Store page.

| Actor | Price | Replies | Notes |
|---|---|---|---|
| clockworks/tiktok-comments-scraper | USD 0.50 per 1,000 comments, SPOT-CHECKED | Yes, `maxRepliesPerComment`, `replyCommentTotal`, but the page says "Successful extraction of all desired replies is currently not guaranteed" | 42,000 users, 99.7% stated success. The safe choice, with that caveat. |
| apidojo/tiktok-comments-scraper | USD 0.30 per 1,000 | Optional, but the listing itself warns "replies may not always come through as expected" | 3,000 users. Cheapest, weakest on the one field this corpus needs. |
| clockworks/tiktok-profile-scraper | USD 1.00 per 1,000 videos | n/a | Ranking tool, see below |
| clockworks/tiktok-scraper | from USD 1.70 per 1,000 videos | via `commentsPerPost` | Flagship, 277,000 users, 97% success |
| devcake/tiktok-search-video-comments | USD 0.60 per 1,000 | NO, one comment per row | 5 users, 85% success. Disqualified. |
| automation-lab/tiktok-comments-scraper | about USD 3.01 per 1,000 effective | Yes, `isReply` and `parentCommentId` | Most expensive checked |

Output on the Clockworks comments actor: text, `diggCount` (likes), `replyCommentTotal`, `createTimeISO`, `uniqueId` (handle), `uid`, `cid`, video URL. Enough for the voc record shape the youtube CLI writes.

**"Most discussed" needs a client-side sort.** No actor sorts a profile by comment count because TikTok's own profile feed does not. The profile scraper's `profileSorting` offers Latest, Oldest, Popular (by likes). Every video row carries `commentCount`, so the path is scrape 100 to 200 videos per profile, sort locally, take the top 20, feed those URLs to the comments actor. This is the same shape as `core.sweep` in the youtube CLI, which ranks over the whole channel for exactly this reason.

**Worked cost, 5 accounts x 20 videos x 200 comments = 20,000 comments.**

| Path | Comments | Ranking | Total |
|---|---|---|---|
| Cheapest (apidojo, 100 videos per profile) | 20 x 0.30 = USD 6.00 | 500 rows = USD 0.50 | USD 6.50 |
| Reliable (Clockworks, 200 videos per profile) | 20 x 0.50 = USD 10.00 | 1,000 rows = USD 1.00 | USD 11.00 |

Both exceed the free plan's USD 5 monthly credit, so one run needs a paid plan or a top-up. And given the sizing above, the real TikTok corpus is two accounts, not five, so the true spend is under USD 5.

**Terms of service.** TikTok's US terms, section 3.4, prohibit users from any attempt to "scrape, crawl, export or otherwise extract any data or content in any form, for any purpose, from the Platform using any automated system or software, including automated 'bots,' except as approved in writing by TikTok USDS Joint Venture" (tiktok.com/legal/page/us/terms-of-service/en). That covers the Apify route on its face. Whether it binds a party that scrapes logged out and never accepted the terms is unsettled and jurisdiction-dependent; the agent reported the text, not its enforceability.

**Not verified by the agent.** Actor last-modified dates (Apify's API returned today's date for every actor, a metadata artefact), full specs for three lesser actors (alien_force, craig337, epctex), and enforceability under Australian law.

## The official Instagram route for iDD's own comments

REPORTED by the third research agent, read 2026-09-11, and consistent with what the Meta
connection showed in this session.

**Own media, full thread.** `GET /{ig-media-id}/comments` on the Instagram Graph API returns
top-level comments (max 50 per page), and "Replies to comments are not included unless you
use field expansion to request the replies field"; replies also have their own edge,
`GET /{ig-comment-id}/replies`. Fields include id, text, timestamp, and by field selection
username and like_count (the last two corroborated by developer guides, UNVERIFIED against
the primary reference in the agent's pass). Permissions are the 2025-renamed
`instagram_business_basic` and `instagram_business_manage_comments` (formerly
`instagram_basic` and `instagram_manage_comments`).

**No App Review for own-account reads.** Standard Access covers accounts the app's role
holders own or manage. A company reading comments on its own posts does not need Live mode
or App Review; a System User token from Business Manager is the documented pattern for an
unattended script, a long-lived user token also works. The agent could not fetch Meta's
Access Levels or System Users pages directly (both moved, HTTP 404), so this rests on
secondary developer sources describing them. Marked well-corroborated, not primary-verified.

**Other accounts' media, text is never available.** Business Discovery exposes
`comments_count`, `like_count` and `view_count` on another business account's media and
explicitly "does not grant you permission to access media objects directly - performing a
GET on any returned IG Media will fail due to insufficient permissions" (quoted from the
fetched Meta page). Hashtag Search returns media metadata and counts only, no username, no
comment text, 30 hashtags per rolling week, and needs Advanced Access. Mentions return the
one comment where iDD is tagged, not the thread. **There is no access tier, however much
review is completed, that returns comment text on competitor posts.** That is the whole
reason Apify is on the table for competitors and not for iDD's own account.

**What exists today on this machine.** The Pipeboard Meta Ads MCP sees iDD's Instagram
account but its token predates Pipeboard's instagram_basic grant and fails with Meta error
code 10 on any post read. Even after the reconnect Pipeboard suggests, neither connected
Meta MCP has an Instagram comment-reading tool (Pipeboard's `get_post_comments` is for
Facebook Page posts and ad dark posts). So the official route for iDD's own comments is a
small script against the Graph API with a token from iDD's Business Manager, not an MCP call.

## Legal and account risk

REPORTED by the third research agent, read 2026-09-11. Not legal advice; what the sources say.

**Meta's written terms prohibit it.** Meta's Automated Data Collection Terms define automated
collection to include "web scrapers, bots, robots, spiders, crawlers", permit it only for
search engines, link previews, or "express written permission", and reserve the right to
"implement measures to restrict your Automated Data Collection ... at any time for any
reason" (quoted from the fetched page). The general user terms' "collect data from our
Products using automated means (without our prior permission)" line was quoted via secondary
sources only; Instagram's Terms page did not render for the agent (UNVERIFIED verbatim).

**TikTok's written terms prohibit it.** Section 3.4, quoted in the TikTok section above.

**US case law cuts the other way for logged-out public data.** Meta v. Bright Data
(N.D. Cal., January 2024): summary judgment for Bright Data on breach of contract because
Meta's terms bind logged-in users, and logged-out scraping of public pages is not a breach;
Meta then dismissed its remaining claim and waived appeal. As of the latest evidence found
(August 2026) it is closed and stands as persuasive US precedent. hiQ v. LinkedIn
(9th Cir., 2022): scraping public, no-login pages does not violate the CFAA, though hiQ
later lost a separate contract claim for breaching LinkedIn's user agreement with fake
accounts and settled. Neither is Australian law.

**Enforcement pattern.** Meta has sued and settled with scraping SERVICES (Voyager Labs,
BrandTotal, Unimania), all of which used fake or logged-in accounts. No enforcement by Meta
or TikTok against Apify by name was found (absence of evidence, not proof). **No source was
found of Meta suspending the account of a business that merely bought scraped public data**
from a vendor; the agent flagged that as a genuinely open question, not a low-risk finding.

**Where the exposure sits.** With logged-out actors, no iDD or Pro Marketing credential
touches the scrape, so the direct account-suspension vector (a detected login) is absent.
The residual exposure is contractual and reputational, and under Apify's terms it sits
entirely with the customer, with an indemnity running to Apify.

**Australian Privacy Act.** The OAIC is unambiguous that "Even if personal information is
publicly available (for example, if it's published on social media...), it is still covered
by the Privacy Act", and under APP 3 public availability "does not allow it to be collected
and used in whatever way the APP entity chooses". A comment plus handle is personal
information. APP 5 notification to each commenter is the friction point nobody solves for
scraped strangers. The small business exemption (under AUD 3 million turnover) was still in
force on 2026-09-11; the 2024 amendment act did not remove it and the second tranche is at
exposure-draft stage. Whether iDD sits under that threshold is a fact Julian knows and this
document does not record. Note the existing YouTube corpus already carries commenter handles
under the same Act, collected through a sanctioned API; the handle policy (kept in raw JSON,
never copied into synthesis or copy) already exists and would apply unchanged.

**The rule this collides with.** The voc-research skill's own capture-paths reference, written
in this stream on 2026-09-09, says: "Where a source publishes an API, use it rather than
defeating a block. A block is the publisher setting terms... Reading threads in a signed-in
browser the way any member would is fine. Bulk extraction against a block is not." The
reddit-plugin was built on exactly that principle and its CLAUDE.md forbids "an Apify actor
bolted on when the API 403s". Instagram publishes an API that deliberately withholds
competitor comment text, and its logged-out post page hides comments behind a sign-up wall.
An honest reading is that Apify on competitor Instagram is bulk extraction around a
publisher's stated limit, whatever the US courts say about contract formation. Adopting it
means either amending that rule with a reasoned exception or accepting the inconsistency.
This is the strongest argument against, and it is Julian's rule, not an outside one.

## Options and recommendation

**Option A, official route for iDD's own Instagram comments.** Free, sanctioned, needs a Graph
API token from iDD's Business Manager (Julian or whoever administers it) and a small script.
Yield unknown until run; iDD's account has about 33,000 followers and its YouTube comments
were the richest single source in the existing map, so the prior is good. No policy conflict.
Do this regardless of anything else below.

**Option B, Apify for the four competitor Instagram accounts.** About USD 10 of actor spend on
scrapesmith plus one month of Starter (USD 19), or USD 40 to 50 on the official actor. Logged
out, no iDD credential involved. Covers the accounts where the audience actually is (34,000
to 87,000 followers each). Against it: Meta's terms, the capture-paths conduct rule, Apify's
indemnity, an unquantified but nonzero chance Meta treats buyers as it treats scrapers, and
the unknown of how much a logged-out actor actually sees. For it: the YouTube map's headline
finding (the abandonment gap) was carried by competitor channels, not iDD's; the same
triangulation is impossible on Instagram any other way; US precedent favours logged-out
public scraping; cost is trivial.

**Option C, signed-in browser for a handful of competitor posts.** The Reddit pattern. Claude
in Chrome, Julian's own session, reading the way any member would. Fits the conduct rule as
written. Does not scale to a 100-post sweep and produces no structured JSON without extra
work, but for "read the 20 most-commented 3Shape posts and pull the sticky lines" it is
viable and policy-clean.

**Option D, TikTok.** Two accounts with any audience (3Shape, iDD). Under USD 5 on Clockworks.
Same terms problem as Instagram, weaker yield, and the actor itself warns reply extraction is
not guaranteed. Not worth its own build; if B goes ahead, TikTok is a second actor call in
the same tool, otherwise skip it.

**Recommendation.** Run A now, it is free and clean. Do not build B until Julian has decided
the policy question with the capture-paths rule in front of him; if he says yes, build it as
a standalone plugin in the youtube and reddit shape (thin CLI on `apify-client`, same voc
record, `clients.toml`, an audit line on every record naming the actor and that it ran logged
out, never a fallback inside reddit-plugin), pilot on one competitor account for about USD 2
before the full sweep, and amend the capture-paths rule with the reasoned exception so the
skill stops contradicting the tool. If he says no, C covers the top posts by hand and the
rule stands. Either way, TikTok rides along or is dropped; it does not earn a decision of its
own.

**Confidence.** High on the inventory, the official-API limits and the prices (all read
live). Medium on the actor yield (logged-out surfaces vary and nothing was run). Low on
the enforcement question for buyers of scraped data (no evidence either way). The one fact
that would change the analysis is a documented case of Meta acting against a business for
using vendor-scraped public data; none was found.

**Priority, restated.** Both platforms sit at the sixth source tier with YouTube. The map's
top gap is still sales-call VOC from Fireflies and Granola, which needs no policy decision
and no spend. This evaluation answers a question; it does not move that gap.

## Questions Julian needs to answer

1. Policy. Given Meta's and TikTok's written terms and the conduct rule in the voc-research
   capture-paths reference, is Apify on competitor Instagram a yes (build, pilot, amend the
   rule), a no (Option C by hand), or a not-now?
2. Official route. Who generates the Graph API token for iDD's Instagram (Business Manager
   system user under the iDD business), or should the Pipeboard connection be reconnected
   first so the MCP at least sees posts, even though it cannot read Instagram comments?
3. TikTok. Ride along with B, or drop.
4. Tool shape, if B is a yes. Standalone plugin (working name undecided) mirroring youtube
   and reddit, or a script inside idd-world research. The standalone is the recommendation
   because Pro Marketing clients would use it too, the same reason youtube-plugin is standalone.
5. Privacy. Does iDD sit under the AUD 3 million small business threshold? This decides
   whether APP 3 and APP 5 bind the collection at all, and it belongs in the corpus README
   either way.

## Decisions, 2026-09-11

Julian answered the questions above in session on 2026-09-11 (late evening AEST).

| Question | Decision |
|---|---|
| Policy on Apify for competitor Instagram | **Pilot one account first.** Build the tool, run one account inside the free USD 5 credit, read the yield, then decide the full sweep. Amend the capture-paths conduct rule with a reasoned exception. |
| iDD's own Instagram comments | **Julian generates the Business Manager token** with the Instagram comment scopes and puts it in 1Password. A script is written against it. |
| TikTok | **Rides along with Instagram.** |
| Targets | **Widen beyond the four scanner brands.** Find other dental education accounts on Instagram and TikTok with good followings and engagement to test on. |
| Purpose, in Julian's words | "our main thing is to find what people are complaining about their challenges in dentistry and how that will tie in with the courses we offer or need to develop or acquire or partner on" |
| Tool shape | **Standalone plugin**, the youtube and reddit shape. |
| Build | social-plugin 0.1.0 built 2026-09-11 at ~/code/social-plugin; spec and plan under its docs/superpowers. Pilot not yet run. |

The purpose line changes the target selection. The four scanner brands were chosen for the
YouTube corpus because scanner buyers narrate purchase decisions under review videos. For
"challenges in dentistry" mapped to course demand, the richer accounts are the ones where
dentists, assistants and hygienists complain about work: educators, clinical influencers,
dental humour accounts, and assistant and hygienist communities. Candidate discovery is the
first step of the build, before the pilot account is chosen.

## Pilot, 2026-09-12

Julian picked **dentistry_humor** (Instagram, 256K followers, hygienist-run humour
page) over 3Shape, for the widened purpose. Dry run estimate USD 2.34 (200 posts
listed at 0.0017, 4,000 comments at 0.0005, one run fee). He gave the go and the
sweep ran at 03:22 UTC.

| Stage | Actor | Result | Actual USD |
|---|---|---|---|
| Ranking | apify/instagram-post-scraper 0.0.598 | 200 posts listed, `commentsCount` present on all | 0.306 |
| Comments | scrapesmith/instagram-comments-scraper 0.0.168 | run SUCCEEDED, exit 0, **0 items** | 0.00005 |

The comments actor's log: "FREE USER detected: hard capped at 0", "USER LIMIT
REACHED! Dataset has 0 items (limit: 0)". Its README says the same in words; the
evaluation above read the price row and missed the gate. So the pilot produced no
comments and USD 0.306 bought the ranking only.

What the ranking showed, and it changes the sizing: the 20 most-discussed
dentistry_humor posts carry **43,046 comments** between them (top post 11,865, 20th
605; all 200 listed posts, 66,288). The 200-per-post cap, not the account, bounds the
yield. Every one of the 20 is a reel, most tagging @jerry_rdh, on office friction
(phones in the chair, copay complaints, sterilization, assistants administering local
anaesthetic in Oregon and Nevada), which is exactly the complaint register the
widened purpose asked for.

Options put to Julian, with the Free-plan prices read live from each actor's
`pricingInfos`: supreme_coder at USD 0.001 per comment on Free (replies included,
529 users), the official actor at USD 0.0023 on Free (replies for paying users only),
or a plan upgrade keeping scrapesmith at USD 0.0005. **Decision: upgrade to Starter
and keep scrapesmith**, no tool change to the actor wiring. The official actor's
README now quotes Starter at USD 29 a month (the 2026-09-11 read of apify.com/pricing
said USD 19); the console price at upgrade time governs.

Tool consequence, built the same day (social-plugin, unreleased): a paid run that
succeeds with zero items now raises on every paid path, naming the run, the money
already spent, and the actor's own log lines. The tool had reported "20 ranked posts
ended up with no comments" and never said why.

### The second run, on Starter

Julian upgraded in the console (Starter, USD 19 credit a month, so the 2026-09-11 price
read was right after all). Same command, 03:36 to 03:40 UTC.

| Stage | Result | Estimate USD | Actual USD at finish | Settled USD |
|---|---|---|---|---|
| Ranking, 200 posts | 200 listed, `commentsCount` on all | 0.34 | 0.27 | 0.30 |
| Comments, 20 posts x 200 | 4,000 items, all attributed, none unmatched | 2.00005 | 1.90005 | 2.00005 (4,000 items plus one start event) |

Estimate-versus-actual: the comments estimate was exact once billing settled; the
ranking came in under (the post scraper settled at 0.0015 per post on Starter against
the 0.0017 Free tier price configured; the first attempt's ranking, on Free, settled at
exactly 0.34). Whole pilot, both attempts, settled: USD 2.64. Two findings for the tool: `usageTotalUsd` read the moment a run
finishes can lag the settled figure by a minute, so `social spend --refresh` was added;
and scrapesmith returned **no replies at all** (1,396 advertised by `repliesCount`, zero
in `replies`), so the "nested replies" claim in the actor table above held for the output
schema and not for a run. `totals.replies_advertised` now records that gap.

**Yield.** 485 of 4,000 kept by the mechanical prefilter (3,501 under 80 characters,
which is what "popular" order surfaces on a humour page). All 485 read in full. The
corpus is US hygienists and assistants on scope-of-practice bills (Arizona assistants
scaling, Oregon assistants giving local anaesthetic, Nevada on-the-job hygienists), pay,
burnout, DSOs and insurance reimbursement; patients on the cost of extractions and
braces removal; and reactions to the humour. No scanner, CAD/CAM or digital-workflow
voice. Against the map's four gaps: nothing on Pulls of the New, nothing on the
independence objection, no sales-call VOC; the assistant persona gains a strong second
channel (the register matches: overworked, underpaid, blamed) but on scaling and
anaesthesia, not scanning. One course-demand signal iDD does not serve: assistants
asking for a real certification pathway to anaesthesia and scaling.

**Decision the pilot supports.** The pipeline works and the price is as estimated; the
account was the wrong one for the scanner map and the right one for "what dental staff
complain about". The next paid sweeps should be the digital-education comparators and
the scanner brands (digitaldentalacademy, dentistry.ohis, exocadofficial, 3shape), which
is where course-relevant voice will be. Julian's call on which, and on whether a second
humour or hygienist account is worth about USD 2.30 for the persona alone.

### Four more accounts the same afternoon

Julian named dr.mostafa.salah, dr.wallyrenne, drmichaeldefee and themodinstitute (all
verified live in the in-app browser, 134K, 52.3K, 27.8K and 27.2K followers, all digital
dentistry educators) and said "Do all four and go back to 50 posts each, unlikely to
have over 200 comments on any of their posts". The tool's cap was raised from USD 5 to
USD 19 because the estimate is a ceiling (5.34 per account at 50 posts) and the guard
refuses on the ceiling.

| Account | Comments | Kept | Ranking USD | Comments USD | Ceiling |
|---|---|---|---|---|---|
| dr.mostafa.salah | 2,644 | 4 | 0.30 | 1.32 | 5.34 |
| dr.wallyrenne | 1,432 | 132 | 0.30 | 0.72 | 5.34 |
| drmichaeldefee | 1,852 | 177 | 0.30 | 0.93 | 5.34 |
| themodinstitute | 583 | 50 | 0.30 | 0.29 | 5.34 |

Settled figures; every comments run billed exactly 0.0005 per item, every Starter
ranking 0.30. Julian's reading was right: no account had 200 comments on a post, so
actual spend was 8 to 30 percent of the ceiling. Day total, both pilot attempts and all
five accounts, USD 7.10 settled.

Two things the sweeps taught beyond the pilot. dr.wallyrenne and drmichaeldefee post
collaboratively, so 101 kept records (31 posts) came back under both handles and were
paid for twice; corpora must be deduplicated on comment id before anything is counted
across files. And dr.mostafa.salah's audience is Arabic-speaking dental students
leaving reactions under 20 characters; 2,644 comments produced four usable English
lines, the worst yield of the day and not a target for an English corpus.

**Verdict on yield.** The MOD Institute trio is the digital dentistry voice the YouTube
corpus lacked: dentists asking which resin, which printer, exocad settings, how long to
design and print, post-processing and curing steps, material longevity; course
questions aimed at MOD Pro; scepticism about printed restorations; alumni testimonials
and an Australian MOD faculty appointment. That is course-relevant voice and competitor
intelligence at once, for about USD 1 per account. dentistry_humor is the assistant
persona's second channel and nothing else. The pipeline, the prices and the cap all
behaved; the two remaining tool gaps are replies (none returned by this actor on any
of the five accounts) and a free re-shape from an existing Apify dataset so a lower
length floor or another language does not cost a second run.

### Four more accounts the same evening, Julian's pick

Offered the map synthesis or the next paid sweep, Julian chose the sweep, and from the
seven obvious candidates (the three digital-education comparators plus the four scanner
brands the 2026-09-11 brief had excluded) took the three comparators plus 3shape as a
triangulation check on the abandonment finding. All seven were read live, logged out,
before the dry runs were shown; every dry run read the same ceiling, USD 5.34005 at 50
posts from a 200 pool. The four ran sequentially, 13:22 to 13:35 UTC, into a fresh
idd-world worktree via `--out`.

| Account | Comments | Kept | Ranking USD | Comments USD | Replies advertised |
|---|---|---|---|---|---|
| digitaldentalacademy | 29 | 3 | 0.30 | 0.01455 | 5 |
| dentistry.ohis | 215 | 1 | 0.30 | 0.10755 | 193 |
| exocadofficial | 1,043 | 47 | 0.30 | 0.52155 | 734 |
| 3shape | 229 | 20 | 0.30 | 0.11455 | 105 |

Settled figures from `social spend --refresh`; at-finish read 0.288 against 0.30 on
three of the four rankings again. Session total USD 1.96, cycle USD 9.07 of 19. Every
comments run billed exactly 0.0005 per item plus the 0.00005 start. Replies again zero
returned on every account.

**What the four taught about picking accounts.** Follower count predicts nothing.
IDDA (35.9K) and OHI-S (29.4K) are institutional feeds whose most-discussed posts carry
6 and 58 comments, nearly all reactions; USD 0.31 and 0.41 bought 3 and 1 records, and
the fixed USD 0.30 ranking stage is the whole cost of a dud, unavoidable without a free
pre-probe of comment counts (the logged-out profile page does not expose them as
text). exocadofficial (108K) turned out to be a network of 26 collaborating designers
and clinicians, which is where the sentences were: 47 records of exocad workflow voice
and course demand at USD 0.82. 3shape (86.5K) gave 20 records that are the abandonment
finding from a second channel of the same brand (support, repair waits, a years-old
feature request, the Chinese-scanner price push) for USD 0.41, and one of its pool posts
is a 3Shape collaboration with iDD's own account. Two exocad records carry commenter
email addresses inside the comment text; the corpus README records that they must not
be copied out. Cross-file overlap grew: exocad shares five records with the MOD files
through the same collaborative posts, so the dedupe-on-id rule applies across all nine
files (919 records, 805 unique).

**Tool consequence.** None required; the pipeline, the guard, the ledger and the
settled-versus-at-finish refresh all behaved. One idea for the backlog: a per-post
`comment_count` distribution printed after the ranking stage and before the comments
stage, so a thin pool (top post under, say, 20 comments) can be stopped before the
comments run, which would not have saved the ranking cost on IDDA but would have made
the dud visible a minute earlier.

### The replies probe and the free re-shape, 2026-09-13

Two half-cent probes settled the replies question. Target: drmichaeldefee's post
DVLoiFnDrAc, whose 200-comment pull in the afternoon sweep advertised 217 replies and
returned none, and which carries 35 filed Persona C lines. Ten comments each.

| Probe | sortOrder | Advertised replies | Returned | Settled USD |
|---|---|---|---|---|
| 5bBSMGCYfJt9K1RvK | recent | 0 | 0 | 0.00505 |
| aG9j0xC9oxDAz4nj5 | popular | 71 | 0 | 0.00505 |

The first attempt did not run at all: Apify rejected `sortOrder = "recent_activity"`
with HTTP 400 `invalid-input` before any money moved. The actor's input schema
enforces `["popular", "recent"]`; the value the tool carried since 2026-09-11 came from
the field's own description text, which still says `'recent_activity'`. Fixed in
social-plugin (the enum is now pinned by a test) and recorded in its CLAUDE.md.

**Verdict.** scrapesmith never fills `replies`, whatever the sort order or the cap.
Neither variable the 2026-09-12 handoff named makes a difference. Threads need a
second actor role with its own input builder and normaliser: `supreme_coder/
instagram-comments-scraper` (`scrapeReplies`, USD 0.0003 per comment on a paid plan)
or the official `apify/instagram-comment-scraper` (`includeNestedComments`, replies for
paying plans, which Starter is). Both are priced in the actor table above; neither has
been run. Every Persona C question in the map stays filed without its answer until one
is.

**Tool consequence, built the same day (social-plugin, unreleased).** `--from-run
<run-id>` re-shapes the dataset of an earlier run for free: no actor, no guard, no
ledger entry, provenance stamped from the original run and the audit carrying its
settled cost with a note. Verified by re-shaping the drmichaeldefee run at the default
floor, which reproduced the landed corpus record for record (177 kept of 1,852,
identical drop counts), and at a 40-character floor, which kept 438. The 80-character
floor decision, and dr.mostafa.salah's 2,644 comments in any language, can now be
looked at without a second paid run. Cycle after the probes: USD 9.08 of 19 settled.
