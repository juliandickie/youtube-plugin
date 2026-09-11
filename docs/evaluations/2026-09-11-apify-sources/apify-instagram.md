# Apify for Instagram Comment Scraping - Research Report

Read-only research only. Nothing was signed up for, no actor was run, no account was created. All facts below were read on 2026-09-11 unless otherwise noted. Every fact is sourced with the URL it came from.

---

## 1. Apify Store actors for Instagram comments and posts

### apify/instagram-comment-scraper (official Apify actor)

- Maintainer - Apify (the platform operator itself), source https://apify.com/apify/instagram-comment-scraper, read 2026-09-11
- Pricing model - Pay per event (PAY_PER_EVENT), charged per comment written to the dataset. Source https://api.apify.com/v2/acts/apify~instagram-comment-scraper (public actor metadata API), read 2026-09-11
- Exact live price per comment (tiered by the caller's Apify plan, effective since the 2026-07-14 pricing entry) - Free $0.0026, Bronze $0.0023, Silver $0.0021, Gold $0.0019, Platinum $0.0017, Diamond $0.0014. Minimum charge per run $0.0026. Source as above.
  - Note - the actor's own marketing page states "from $1.90 / 1,000 comments" and references a "Starter plan ($29/month)" giving "over 12,600 comments per month" (https://apify.com/apify/instagram-comment-scraper, read 2026-09-11). That $29/month figure does not match Apify's own platform pricing page (Starter is $19/month, see section 2) - marked UNVERIFIED, likely stale marketing copy on the actor page.
- Cap on comments per post - no hard cap documented. Input parameter `resultsLimit` sets the requested number ("if set to 5, you will get 5 comments per URL"); the actor's FAQ says "the scraper delivers as many comments and replies as it can access" and that "the maximum number of results may vary depending on the complexity of the input, location, and other factors." Source https://apify.com/apify/instagram-comment-scraper/api and the main Store page, read 2026-09-11.
- Replies - yes, but gated: the `includeNestedComments` input parameter is described as "for paying users only. If checked, the scraper will extract replies for each comment." This implies replies are not available on the Free plan. Source https://apify.com/apify/instagram-comment-scraper, read 2026-09-11.
- Output fields - comment ID, post ID, comment text, comment position, timestamp, owner ID, owner verification status, owner username, owner profile picture URL, reply comments, engagement (like count), comment URL. Source Store page, read 2026-09-11.
- Cookies/login - not required. The Store page states "the scraper extracts only the comments shown to Instagram users who are not logged in," i.e. it runs logged out and therefore only sees what a logged-out visitor sees. Source as above.
- Last modified - 2026-09-11T11:23:29.618Z (modifiedAt field). Created 2021-11-25. Source https://api.apify.com/v2/acts/apify~instagram-comment-scraper, read 2026-09-11.
- Users - 53,166 total users, 4,821 monthly (30-day) users, 9,958 90-day users, 9,915,568 total runs. Source as above.
- Success rate / rating - 100.0% run success rate shown on the Store page; 4.66/5 rating from 67 reviews. Source https://apify.com/apify/instagram-comment-scraper, read 2026-09-11.

### apify/instagram-scraper (official, general-purpose actor covering profiles/posts/reels/comments/hashtags/places)

- Maintainer - Apify. Source https://apify.com/apify/instagram-scraper, read 2026-09-11
- Pricing model - Pay per event, tiered per "Result" (any item type - post, reel, comment, profile, etc). Source https://api.apify.com/v2/acts/apify~instagram-scraper, read 2026-09-11
- Exact price per result (tiers, active since 2026-02-20) - Free $0.0027, Bronze $0.0023, Silver $0.0019, Gold $0.0015, Platinum $0.0009, Diamond $0.0005. Minimum charge $0.0027. Source as above.
- Cap on comments per post - the Free plan is explicitly capped: "only the top 15 comments sorted by newest" per post. Paid plans get "full access to comment threads." Source https://apify.com/apify/instagram-scraper, read 2026-09-11.
- Replies - available on paid plans via `includeNestedComments: true`; not available (or limited) on Free. Source as above.
- Output fields (post-level sample) - id, shortCode, caption, hashtags, mentions, likesCount, commentsCount, timestamp, ownerUsername, displayUrl, videoUrl, musicInfo, childPosts, plus a nested comments array. Source as above.
- Cookies/login - not required; scrapes public data via Instagram's logged-out surfaces (an "unofficial API," since Instagram restricted its official API access in 2020). Source as above.
- Last modified - 2026-09-11 (modifiedAt). Created 2019-04-30. Source https://api.apify.com/v2/acts/apify~instagram-scraper, read 2026-09-11.
- Users - 390,569 total, 42,838 in the last 30 days, 192,105,979 total runs. Source as above.
- Success rate / rating - 100.0% success rate; 4.70/5 from 593 reviews. Source https://apify.com/apify/instagram-scraper, read 2026-09-11.

### apify/instagram-post-scraper (official, posts only)

- Maintainer - Apify. Source https://apify.com/apify/instagram-post-scraper, read 2026-09-11
- Pricing model - Pay per event, two chargeable events: "Post" (each post row) and "Post-Details" (an enrichment sub-event). Effective 2026-07-13. Source https://api.apify.com/v2/acts/apify~instagram-post-scraper, read 2026-09-11
- Exact prices - Post event: Free $0.0017, Bronze $0.0015, Silver $0.0013, Gold $0.0010, Platinum $0.0008, Diamond $0.0004. Post-Details event: Free $0.0010, Bronze $0.0008, Silver $0.0007, Gold $0.0006, Platinum $0.0002, Diamond $0.0001. Minimum charge per run $0.005. Source as above.
- Cap on comments per post - this actor is post-focused; it returns only "first and latest comments" (a small preview, not a full comment set) per post, not a configurable deep comment pull. No numeric cap stated beyond "first and latest." Source https://apify.com/apify/instagram-post-scraper, read 2026-09-11.
- Replies - limited; only latest-comment replies are embedded in the post output, not a full reply tree. Source as above.
- Output fields - post URL, author, caption, hashtags, mentions, likes count, comments count, image/video URLs, alt text, post type, timestamp, tagged users, video duration, view counts, sponsored/pinned flags, plus the embedded first/latest comment data. Source as above.
- Cookies/login - not required; public posts only, private accounts inaccessible. Source as above.
- Last modified - 2026-09-11 (modifiedAt). Created 2021-11-24. Source https://api.apify.com/v2/acts/apify~instagram-post-scraper, read 2026-09-11.
- Users - 126,879 total, 11,783 in the last 30 days, 52,246,189 total runs. Rating 4.29/5 from 139 reviews, 100% success rate. Source https://apify.com/apify/instagram-post-scraper, read 2026-09-11.

### apify/instagram-reel-scraper (official, reels only)

- Maintainer - Apify. Source https://apify.com/apify/instagram-reel-scraper, read 2026-09-11
- Pricing model - Pay per event, five chargeable events: Reel, Actor Start, Shares Count, Transcript, Video Download. Effective since 2026-03-11 (per api.apify.com, "Modified" 2026-09-11). Source https://api.apify.com/v2/acts/apify~instagram-reel-scraper, read 2026-09-11
- Exact prices - Reel: Free $0.0026, Bronze $0.0023, Silver $0.0014, Gold $0.0010, Platinum $0.0008, Diamond $0.0004. Actor Start (one-time per run): flat $0.001 on every tier. Shares Count (per reel with shares data): Free $0.007 down to Diamond $0.002. Transcript (per started minute): Free $0.048 down to Diamond $0.010. Video Download (per started MB): Free $0.020 down to Diamond $0.007. Minimum charge per run $0.0073. Source as above.
- Cap on comments per post - reels carry only "up to 10 latest comments with replies, likes, and timestamps" embedded in the reel record; the Store page explicitly says "for comprehensive comment scraping, users can employ the separate Instagram Comments Scraper." Source https://apify.com/apify/instagram-reel-scraper, read 2026-09-11.
- Replies - yes, within that 10-comment preview only.
- Output fields - id, caption, hashtags, mentions, url, likesCount, commentsCount, videoViewCount, videoPlayCount, timestamp, videoUrl, musicInfo, taggedUsers, latestComments (nested array), optional transcript/downloadedVideo, location, co-authors, sponsorship flags, dimensions. Source as above.
- Cookies/login - not required; accesses the logged-out version of the page. Source as above.
- Last modified - 2026-09-11 (modifiedAt). Created 2022-11-23. Source https://api.apify.com/v2/acts/apify~instagram-reel-scraper, read 2026-09-11.
- Users - 142,797 total, 12,536 in the last 30 days, 14,582,886 total runs. Rating 4.39/5 from 102 reviews, 100% success rate. Source https://apify.com/apify/instagram-reel-scraper, read 2026-09-11.

### Top third-party alternatives found via Store search for "instagram comments"

Search performed 2026-09-11 against the Apify Store; results included om.shinde, api-empire, scraper-engine, automation-lab, scrapesmith, crawlerbros, supreme_coder, and the official apify actor. The two most relevant credible third-party alternatives checked in depth:

**scrapesmith/instagram-comments-scraper**
- Maintainer - "Scrape Smith" (independent developer). Source https://apify.com/scrapesmith/instagram-comments-scraper, read 2026-09-11
- Pricing model - Pay per event: an "Actor Start" event at $0.00005 (one-time per run) and a "Dataset Result Item" (comment) event at $0.0005, described on the Store page as flat pay-per-result pricing ("$0.50 per 1,000 results"), not tiered by Apify plan. Source https://api.apify.com/v2/acts/scrapesmith~instagram-comments-scraper and https://apify.com/scrapesmith/instagram-comments-scraper, read 2026-09-11.
- Cap on comments per post - configurable via `maxCommentsPerPost`; no hard cap documented, though the page advises targeting posts with at least 10 comments for best results.
- Replies - yes, returned as a nested `replies` array per comment.
- Output fields (14) - postId, postUrl, commentId, commentUrl, text, timestamp, likesCount, userId, username, userFullName, ownerProfilePicUrl, isVerified, repliesCount, replies.
- Cookies/login - none required; stated to work "entirely on public data."
- Last modified - 2026-09-10T09:35:23.403Z; created 2025-10-31. Source https://api.apify.com/v2/acts/scrapesmith~instagram-comments-scraper, read 2026-09-11.
- Users - 2,031 total, 356 in the last 30 days, 90,463 total runs.
- Rating - Store page shows 4.41/5 from 18 reviews and a 100.0% success rate (https://apify.com/scrapesmith/instagram-comments-scraper, read 2026-09-11); the raw api.apify.com metadata pull returned rating 0 / review count 0 for this same actor at the same read. This is an unresolved inconsistency between the two Apify-controlled sources - flagged UNVERIFIED for the exact review count, though the Store page figure is more likely to be current/correct since it renders the public-facing number.

**supreme_coder/instagram-comments-scraper**
- Maintainer - "Supreme Coder" (independent developer). Source https://apify.com/supreme_coder/instagram-comments-scraper, read 2026-09-11
- Pricing model - Pay per event: comment extraction tiered by Apify plan (Free $0.001, Bronze/Silver/Gold/Platinum/Diamond $0.0003 each), plus a one-time Actor Start fee of $0.0005 per run. Effective since 2026-07-30. Source https://api.apify.com/v2/acts/supreme_coder~instagram-comments-scraper, read 2026-09-11.
- Cap on comments per post - none enforced; user sets `limitPerSource`.
- Replies - yes, on by default, toggled via `scrapeReplies`, with configurable thread depth.
- Output fields - comment ID, post URL, media ID, comment text, author username/full name/verification, like count, reply count, mentions, hashtags, ISO and Unix timestamps, edit/rank flags, thread depth, nested replies array.
- Cookies/login - none required, stated explicitly as "no Instagram login or cookies needed."
- Last modified - 2026-08-22T07:16:16.886Z; created 2026-06-24. Source https://api.apify.com/v2/acts/supreme_coder~instagram-comments-scraper, read 2026-09-11.
- Users - 529 total, 169 in the last 30 days, 58,674 total runs. Store page shows 3.63/5 from 4 reviews.

Other Store search hits not investigated in the same depth (named only, not verified): om.shinde/instagram-comments-scrapper, api-empire/instagram-comments-scraper (states it needs a `sessionId` cookie from your own Instagram account - i.e. it is NOT a logged-out scraper), scraper-engine/instagram-comments-scraper (a lead-enrichment variant), automation-lab/instagram-comments-scraper (pay-per-event, $0.005 run start fee, tiered per-comment pricing from $0.0023 free down to about $0.00056 on its top tier, default cap of 20 comments per post, replies optional via `includeReplies` and counted toward the per-comment cost, no login required - source https://apify.com/automation-lab/instagram-comments-scraper, read 2026-09-11), crawlerbros/instagram-comment-scraper (named only, not fetched).

---

## 2. Apify platform plans (read 2026-09-11, source https://apify.com/pricing unless noted)

| Plan | Monthly price | Included platform credit | CU price | Max RAM | Max concurrent runs | Datacenter proxy | Residential proxy |
|---|---|---|---|---|---|---|---|
| Free | $0 | $5/month | $0.20/CU | 16 GB | 5 | 5 IPs included | $8/GB |
| Starter | $19/month ($17/month billed annually) | $19/month | $0.20/CU | 64 GB | 32 | 30 IPs included, then $1/IP | $8/GB |
| Scale | $199/month ($179/month billed annually) | $199/month | $0.16/CU | 256 GB | 128 | 200 IPs included, then $0.80/IP | $7.50/GB |
| Business | $999/month ($899/month billed annually) | $999/month | $0.13/CU | 512 GB | 256 | 500 IPs included, then $0.60/IP | $7.00/GB |
| Enterprise | Custom (contact sales) | Custom | Custom | Custom | Custom | Custom | Custom |

Cross-check on proxy pricing from https://apify.com/proxy (read 2026-09-11): "Datacenter IPs from $0.60 per IP" and "Residential IPs from $8 per GB" - consistent with the Business-tier floor and Free/Starter-tier ceiling above; the proxy page adds "additional charges for data transfer apply" without itemizing them further (UNVERIFIED beyond that statement).

Do pay-per-result/pay-per-event actor charges also consume platform credit - yes. Apify's documentation states plainly that "both models draw on the platform usage credits included in your plan, and excess usage is charged to your next invoice," i.e. running a pay-per-event actor like the ones in section 1 debits the same monthly credit pool shown above rather than being billed on a separate line, until that credit is exhausted, after which it is billed as overage. Source https://apify.com/pricing (platform pricing FAQ text), read 2026-09-11.

---

## 3. Apify's official MCP server and the apify-client Python package

### MCP server (mcp.apify.com)

- Endpoint - `https://mcp.apify.com`, using Streamable HTTP with OAuth as the recommended transport. Source https://docs.apify.com/platform/integrations/mcp, read 2026-09-11.
- Authentication - two supported modes:
  1. OAuth - the user signs in through a browser on first connection, no token in config.
  2. Bearer token - the user's Apify API token (obtained from the API & Integrations section of Apify Console) is passed as an `Authorization: Bearer <APIFY_TOKEN>` header.
- Example client config (e.g. for an MCP-capable desktop client):
```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com",
      "headers": {
        "Authorization": "Bearer <APIFY_TOKEN>"
      }
    }
  }
}
```
- Tools exposed for running an actor and reading its results - `search-actors` (discover actors), `fetch-actor-details` (inspect input/output schema before running), `call-actor` (execute an actor and return run results with an output preview), `get-actor-output` (retrieve the full dataset when it's not included in the preview, with limit/offset/filter parameters). Source https://docs.apify.com/platform/integrations/mcp, read 2026-09-11.
- Note - `apify.com/apify/actors-mcp-server` (the Store-listed "Actor" version) now 308-redirects to `mcp.apify.com`, i.e. Apify has consolidated the actor-based MCP server into the hosted `mcp.apify.com` product. Source: redirect observed fetching https://apify.com/apify/actors-mcp-server, read 2026-09-11.

### apify-client (Python package)

- A minimal call to run an actor and fetch its dataset, quoted from the package's own documented usage:
```python
from apify_client import ApifyClient

client = ApifyClient('MY-APIFY-TOKEN')

# Start an Actor and wait for it to finish.
run = client.actor('apify/hello-world').call(
    run_input={'message': 'Hello, Apify!'},
)
if run is None:
    raise RuntimeError('Actor run was not found.')

# Iterate items from the run's default dataset.
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(item)
```
Source https://pypi.org/project/apify-client/, read 2026-09-11.
- Authentication - the token is passed directly as a string to `ApifyClient(...)`; the docs do not name a standard environment variable in this quick-start example. The token itself is obtained from the Integrations section of Apify Console. The docs warn: "Keep your token secret. It authorizes requests on your behalf and can incur usage costs. Never commit it to source control or expose it to client-side code." Source as above.

---

## 4. Worked cost estimate

Target volume: 5 accounts x 20 posts x up to 200 comments = 20,000 comments.

Requirement: cheapest actor that (a) returns replies and (b) does not require an Instagram login.

Candidates from section 1 that qualify on both counts:
- apify/instagram-comment-scraper (official) - DISQUALIFIED at the Free tier because `includeNestedComments` (replies) is "for paying users only." On a paid tier it would cost 20,000 x $0.0014 to $0.0023 (Diamond to Bronze) = $28.00 to $46.00, plus needing a Starter/Scale/Business subscription in the first place.
- supreme_coder/instagram-comments-scraper - qualifies (no login, replies on by default), $0.001/comment on Free, $0.0003/comment on any paid tier, plus $0.0005 one-time per run.
- scrapesmith/instagram-comments-scraper - qualifies (no login, replies returned), flat $0.0005/comment regardless of plan tier, plus $0.00005 one-time per run.

On the Free plan (no subscription needed), scrapesmith is cheapest: $0.0005/comment vs supreme_coder's $0.0005/item... wait, supreme_coder is $0.001/comment on Free - so scrapesmith is cheaper on Free ($0.0005 vs $0.001). On any paid tier, supreme_coder's $0.0003/comment undercuts scrapesmith's flat $0.0005 - but a paid tier costs at minimum the $19/month Starter subscription, which is not worth it just to shave this one job's cost. For a one-off or occasional monthly pull sized like this, the Free-plan actor is the fair "cheapest overall" comparison.

**Arithmetic (scrapesmith/instagram-comments-scraper, Free plan, no login required):**

- 20,000 comments x $0.0005/comment = $10.00
- Plus a one-time "Actor Start" event per run at $0.00005. If run once per account (5 runs, each fed 20 post/reel URLs): 5 x $0.00005 = $0.00025. If run once per post instead (100 runs): 100 x $0.00005 = $0.005.
- **Total: approximately $10.00 to $10.01** for the full 20,000-comment pull.

This sits comfortably inside the $5/month Free-plan credit only if split across two months, or inside the Starter plan's $19/month included credit in a single month (since the actor charge draws on the plan's platform credit per section 2). It would not require buying proxy GBs separately, since this actor needs no login and no residential proxy is mentioned in its documentation.

**For comparison**, running the same 20,000 comments through the official apify/instagram-comment-scraper actor (which would require a paid plan to unlock replies) at its cheapest published per-comment rate (Diamond, $0.0014) costs 20,000 x $0.0014 = $28.00, before accounting for the cost of reaching Diamond-tier volume discounts or the underlying subscription.

Caveat that affects all of the above - none of the checked actors document a hard, guaranteed per-post comment ceiling; several (official instagram-scraper on Free, instagram-post-scraper, instagram-reel-scraper) explicitly cap or truncate what they return (top 15 newest, "first and latest" only, or 10 latest respectively) unless you use a comments-dedicated actor and a paid tier / requested `resultsLimit`. Actually reaching "up to 200 comments" on a lightly-commented account may simply return fewer rows than requested (charged only for what is actually returned, since these are pay-per-result/pay-per-event, not pay-per-request) - so $10 is a ceiling estimate assuming all 100 posts genuinely have 200+ comments each; on real accounts (especially the smaller competitor accounts) actual comment counts, and therefore actual cost, will likely be lower.

---

## 5. Apify's stated position on scraping Instagram public data and account risk

Official Apify sources (apify.com / docs.apify.com / blog.apify.com):

- Apify's Acceptable Use Policy (https://docs.apify.com/legal/acceptable-use-policy, read 2026-09-11) does not mention Instagram or social-media scraping by name. It prohibits, among other things: "denial-of-service (DDoS) attacks or any other actions that cause undue burden on any servers or infrastructure" (2.1.1), "any fraudulent or deceptive behavior (such as phishing, malware, impersonation, spoofing, ad fraud, click fraud, etc.)" (2.1.3), "any artificial interaction (such as upvotes, shares, etc.)" (2.1.4), "creating fake accounts or deceptive content" (2.1.6), unauthorized resale of platform features (2.1.9), and "engaging in activities that contravene applicable laws, regulations, or the rights of any third party" (2.1.10). Apify reserves the right to "block, delete, or otherwise restrict any non-compliant User or Actor from the Platform or Website without notice." Ordinary read-only public-comment scraping as described in this brief does not appear to fall under any of these prohibited categories, but that is my inference, not an explicit Apify statement.
- Apify's blog post "Is web scraping legal? Yes, if you know the rules" (https://blog.apify.com/is-web-scraping-legal/, published/updated 2026-02-10 per the fetch) takes a general, jurisdiction-by-jurisdiction position rather than an Instagram-specific one: it discusses the hiQ v LinkedIn case (US, public personal data may be permitted under fair use-style reasoning), notes GDPR treats public personal data as still protected in the EU ("it does not matter at all where the data comes from"), notes California's CPRA treats previously-public personal data differently, and flags that clickwrap Terms of Service are more enforceable than browsewrap ones. It carries the disclaimer "We are lawyers, but we are not your lawyers... For professional legal advice, please talk to a certified lawyer in your country." Apify's COO Ondra Urban is quoted elsewhere summarizing the company's general public stance as "web scraping is neither legal nor illegal. It's how you use it and what you scrape" (found via web search, original interview source not directly verified by me - UNVERIFIED as to primary source).
- Apify's own Instagram Scraper Store page (https://apify.com/apify/instagram-scraper, read 2026-09-11) frames its actors as collecting "only data that is publicly available on Instagram," implicitly positioning itself as a logged-out, public-data-only tool, consistent with all five actors checked in section 1 (none require Instagram login).
- There is an open community question directly on the official actor asking "Does it comply with Instagram's terms and conditions?" at https://apify.com/apify/instagram-scraper/issues/does-it-comply-with-xGNlYjplqUvcFOrmz - I could not retrieve a substantive maintainer answer from that page (the fetch returned only the surrounding Store page chrome, not the issue thread content) - marked UNVERIFIED, worth a manual look before relying on it.

Third-party context (NOT Apify's own words - flagging clearly because it is easy to mistake for official content):
- use-apify.com is an independent, third-party content/affiliate site. Per its own disclosure pages (https://use-apify.com/about, https://use-apify.com/affiliate-disclosure, read 2026-09-11) it is "not owned, operated, or endorsed by Apify Technologies s.r.o." and earns its primary affiliate revenue by promoting Apify. Its article on Apify/scraping legality (https://use-apify.com/docs/what-is-apify/is-apify-legal) cites the January 2024 Meta v. Bright Data ruling (Judge Edward Chen, N.D. Cal.) as holding that Meta's Facebook/Instagram terms "do not bar logged-off scraping of public data," and argues that staying logged out is "the most legally defensible mode for public-page scraping." This is third-party legal commentary, not an Apify policy statement, and should be treated as one commentator's read of the case law, not verified against the court filing itself.
- Apify's own blog post on scraping Instagram specifically (https://blog.apify.com/scrape-instagram-python/, published 2025-07-01, read 2026-09-11) is mostly technical rather than legal: it documents that "Instagram is notoriously aggressive when it comes to detecting and blocking automated requests," that logged-out visits from a VPN or datacenter IP will often hit a login wall even on public pages, and that "many interactions are only accessible to logged-in users." Its brief legal FAQ line states "Yes, it's legal to scrape Instagram as long as you extract data only from public profiles," with the caveat to "take great care when scraping data behind a login, personal data, intellectual property, or confidential data."
- A second, newer Apify blog post (https://blog.apify.com/scrape-instagram-posts-comments-and-more-21d05506aeb3/, published 2026-06-02, read 2026-09-11) notes specifically that "comments and infinite scroll were once public. That data is no longer available without a login" for the general-purpose scraper, and repeats "scraping publicly available data is legal, but you need to be careful not to extract content that is protected by copyright or contains personal information."

Bottom line for the marketing team's use case (read-only, logged-out, public comment text on their own account plus four competitors, comparable in spirit to the YouTube VOC pull they already run): Apify positions all the checked Instagram actors as operating on logged-out/public data only, and states this is generally legal in the relevant case law it cites; the practical account risk is Instagram detecting and blocking/soft-blocking the scraping IP (addressed by Apify's own proxy infrastructure, not by the user's own Instagram account, since no login is used), not an Apify account suspension, since none of the Acceptable Use Policy's prohibited categories describe this kind of read-only public-data pull. No Apify source directly and explicitly states "scraping Instagram will never get your Apify account suspended" - that is my synthesis from the policy text, not a direct quote, and should be read as inference rather than a guarantee.
