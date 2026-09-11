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
| scrapesmith/instagram-comments-scraper | USD 0.50 per 1,000, flat, plus USD 0.00005 per run. SPOT-CHECKED | Yes, nested `replies` array and `repliesCount`. SPOT-CHECKED | `maxCommentsPerPost`, no hard cap | 2,000 users, 90,000 runs, 100% stated success, 4.41 from 18 reviews, created 2025-10-31 |
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
