# TikTok Comment Data for Voice-of-Customer Research - Route Analysis

Research date - 2026-09-11. Read-only research, no signups, no actor runs, no accounts created.

## 1. TikTok's official APIs

TikTok publishes several developer products. None of them let a commercial Australian marketing team pull comments off other accounts' videos, and only one of them (Research API) can return comments at all, and it is closed to commercial applicants.

### Research API - the only official API that returns comment text

Endpoint `/v2/research/video/comment/list/` returns comment fields id, text, video_id, parent_comment_id, like_count, reply_count, create_time, display_name, and redacts personal information found in comment text ("Personal information (phone number, email and credit card account, etc) in the comments will be redacted").
Source - https://developers.tiktok.com/docs/en/research-api-specs-query-video-comments (read 2026-09-11)

Eligibility, quoted verbatim from the official product page -

"Be located in an eligible region and be affiliated with an eligible organization: Academic institutions in the U.S., EEA, UK, Canada, or Switzerland; or Not-for-profit and/or independent research institution, organization, association, or body in the EU."

"Academic institutions or not-for-profit organizations based in Brazil and looking to study online youth safety" may also apply.

"Be independent of commercial interests and able to conduct research on a not-for-profit or non-commercial basis in pursuit of a public-interest mission."
Source - https://developers.tiktok.com/products/research-api (read 2026-09-11)

The FAQ makes the exclusion of commercial applicants explicit, in a direct Q and A -

"I am a creator, advertiser, or commercial user. Am I eligible for access to the Research Tools? No."
Source - https://developers.tiktok.com/doc/research-api-faq (read 2026-09-11)

**Verdict for a commercial Australian agency** - not eligible, on two independent grounds: Australia is not in the eligible region list (US, EEA, UK, Canada, Switzerland, or Brazil-for-youth-safety-only), and Pro Marketing / iDD are commercial entities, which the eligibility text excludes by definition ("independent of commercial interests," "not-for-profit or non-commercial basis"). This would apply equally to the team's own videos and to competitors' videos - the Research API is not scoped by "your account vs other accounts," it is gated by researcher status entirely.

### Display API - metadata only, own-account only, no comments

The Display API exposes `/v2/user/info/`, `/v2/video/list/`, and `/v2/video/query/`. These require OAuth login via Login Kit, with scopes `user.info.basic` and `video.list`, and only return video metadata (id, title, description, duration, cover image URL, embed link) for the account that has authorized the app via login. It has no comment endpoint at all - comments are only exposed by the Research API's separate `/v2/research/video/comment/list/` endpoint.
Sources - https://developers.tiktok.com/docs/en/display-api-overview, https://developers.tiktok.com/docs/en/scopes-overview, https://developers.tiktok.com/docs/en/display-api-get-started (read 2026-09-11)

**Verdict** - (a) the team's own videos - yes for metadata (views, likes, video list) after the team logs in and authorizes the app, but it cannot return comments at all, on any account. (b) other accounts' videos - no, it can only read data for an account that has completed the OAuth authorization flow into your app; a competitor is never going to authorize your app.

### Content Posting API - publishing only, not a read API

This product is described on TikTok's own product page as letting apps "post content or upload drafts from your app to their TikTok profiles." It is a one-way publish channel (captions, hashtags, privacy settings) for an account that has authorized your app. It has no comment-reading capability; nothing in its documentation describes fetching engagement or comment data back.
Source - https://developers.tiktok.com/ (product list) and https://developers.tiktok.com/products/content-posting-api/ (read 2026-09-11)

**Verdict** - not relevant to comment collection at all, for own or other accounts.

### Commercial Content API - ads transparency, not video comments

This product returns ad transparency data (published date, last seen date, targeting information, number of people who saw the ad, advertiser info, disapproved-ad details), initially EU-only data, open to "the public and researchers" regardless of applicant location, via a TikTok for Developers application approved in about two working days. It does not expose comments on organic videos.
Source - https://developers.tiktok.com/products/commercial-content-api (read 2026-09-11)

**Verdict** - not applicable; this is an ad-library product, not a comments API.

### Summary table - official APIs

| API | Returns comments | Own videos | Other accounts' videos | AU commercial company eligible |
|---|---|---|---|---|
| Research API | Yes | Yes if eligible | Yes if eligible | No (region + commercial-status excluded) |
| Display API | No | Metadata only, after OAuth login | No | N/A, no comments |
| Content Posting API | No (publish only) | N/A | No | N/A |
| Commercial Content API | No (ads only) | N/A | N/A | N/A for this use case |

**Bottom line** - there is no official TikTok API route open to this team for the stated task. The only API that returns comment text is closed to commercial companies and to Australia.

## 2. Apify Store actors for TikTok comments and videos

All pricing below is the actor's advertised list/default rate as shown on the Apify Store listing and its pricing tab, read 2026-09-11. Apify's "pay-per-event" actors typically show a tiered price by subscription plan (Free through Diamond); the figures below are the standard/list rate quoted on the store page unless noted. Actor code "last modified" timestamps returned by Apify's public API consistently showed the date of this research (2026-09-11 UTC) for every actor checked, which reads as a metadata artifact of the API query rather than a genuine last-code-change date - treat all "last modified" figures below as UNVERIFIED.

### clockworks/tiktok-comments-scraper ("TikTok Comments Scraper")
- Maintainer - Clockworks
- Pricing model - Pay per result
- Price - $0.50 per 1,000 comments (confirmed on both the Store page and the actor's dedicated Pricing tab)
- Cap on comments per video - no hard cap stated; actual volume "may differ" due to TikTok API limitations; controlled by `commentsPerPost` / `topLevelCommentsPerPost`
- Replies - yes, via `maxRepliesPerComment`; reply count exposed via `replyCommentTotal`
- Output fields - comment text, `diggCount` (likes), `replyCommentTotal`, `createTimeISO` (timestamp), `uniqueId` (commenter handle), `uid` (user id), `cid` (comment id), video URL, avatar thumbnail
- Login/cookies needed - not stated as required; scrapes public data
- Last modified - UNVERIFIED (see note above)
- Users - 42,419 total, 4,077 monthly
- Success rate - 99.65-99.7% (30-day run stats)
Sources - https://apify.com/clockworks/tiktok-comments-scraper, https://apify.com/clockworks/tiktok-comments-scraper/pricing, https://apify.com/clockworks/tiktok-comments-scraper/input-schema, https://api.apify.com/v2/acts/clockworks~tiktok-comments-scraper (all read 2026-09-11)

### clockworks/tiktok-scraper ("TikTok Scraper", flagship/full actor)
- Maintainer - Clockworks
- Pricing model - Pay per event (per-video and per-comment sub-events tiered by subscription plan)
- Price - from $1.70 per 1,000 results (video-level)
- Comment counts - yes, returns `commentCount` per video, and can pull comments per post via `commentsPerPost`
- Output fields (video-level) - `diggCount`, `shareCount`, `playCount`, `collectCount`, `commentCount`, author profile data, video metadata (duration, dimensions, cover URL), hashtags/mentions, music data, timestamp, location
- Login/cookies needed - not stated as required
- Last modified - UNVERIFIED
- Users - 277,511-277,513 total, 22,428 monthly
- Success rate - 96.8-97.2%
Sources - https://apify.com/clockworks/tiktok-scraper, https://api.apify.com/v2/acts/clockworks~tiktok-scraper (read 2026-09-11)

### clockworks/free-tiktok-scraper ("TikTok Data Extractor")
- Maintainer - Clockworks
- Pricing model - Pay per event
- Price - from $1.00 per 1,000 results (with add-on charges for comments extraction reported separately at $0.00015-$0.00125 per comment depending on plan tier)
- Comment counts per video - yes, `commentCount` field present, `commentsPerPost` parameter controls how many comments are pulled per video, usable to help rank/sort videos client-side
- Login/cookies needed - not stated as required
- Last modified - UNVERIFIED
- Users - 55,631 total, 2,803-2,919 monthly
- Success rate - 98.6-98.7%
Sources - https://apify.com/clockworks/free-tiktok-scraper, https://api.apify.com/v2/acts/clockworks~free-tiktok-scraper (read 2026-09-11)

### clockworks/tiktok-profile-scraper ("Tiktok Profile Scraper") - the ranking tool, see section 3
- Maintainer - Clockworks
- Pricing model - pay per event / pay per result
- Price - from $1.00 per 1,000 results
- Login/cookies needed - not stated as required
- Last modified - UNVERIFIED
- Users - 39,923 total, 5,698 monthly
- Success rate - 99.24-99.5%
Source - https://apify.com/clockworks/tiktok-profile-scraper, https://api.apify.com/v2/acts/clockworks~tiktok-profile-scraper (read 2026-09-11)

### apidojo/tiktok-comments-scraper ("TikTok Comment Scraper")
- Maintainer - Api Dojo
- Pricing model - Pay per event / pay per result
- Price - $0.30 per 1,000 comments (confirmed on the actor's Pricing tab; the Apify API metadata additionally shows a historical tiered progression from $0.0001/comment in Dec 2023 up to the current $0.0003/comment, i.e. $0.30/1,000, from Nov 2024 onward)
- Cap on comments per video - no explicit maximum found; store guidance recommends targeting videos with at least ~10 comments per URL to avoid blocking
- Replies - yes, optional via `includeReplies`, but the listing itself notes "replies may not always come through as expected" - a reliability caveat
- Output fields - comment id, text, creation timestamp, like/reply counts, language, parent post id/URL, commenter username, user id, avatar URL, verification status, follower count (if public)
- Login/cookies needed - no, works with public video URLs only
- Last modified - UNVERIFIED
- Users - 3,180 total, 458 monthly
- Success rate - approx 98-99.6%
Sources - https://apify.com/apidojo/tiktok-comments-scraper, https://apify.com/apidojo/tiktok-comments-scraper/pricing, https://api.apify.com/v2/acts/apidojo~tiktok-comments-scraper (read 2026-09-11)

### devcake/tiktok-search-video-comments ("TikTok Video & Comments Scraper")
- Maintainer - devcake
- Pricing model - Pay per event
- Price - $0.60 per 1,000 results
- Cap on comments per video - configurable, default 100, max 1,000
- Replies - **no** - "collects one comment per entry"; reply counts are shown but full reply threads are not returned. This disqualifies it for the brief's requirement to know whether a comment is a reply.
- Output fields - videos table (caption, creator, views, likes, comments, shares, saves, link, publish date, length) and comments table (text, commenter details, likes, reply count, language, pinned status, source video link)
- Login/cookies needed - no
- Last modified - UNVERIFIED
- Users - 5 total, 3 monthly (very low adoption - a reliability flag in itself)
- Success rate - 85.3% (notably lower than the Clockworks/apidojo actors)
Source - https://apify.com/devcake/tiktok-search-video-comments (read 2026-09-11)

### automation-lab/tiktok-comments-scraper ("TikTok Comments Scraper")
- Maintainer - Stas Persiianenko / Automation Lab
- Pricing model - Pay per event (a flat run-start fee plus a per-comment fee)
- Price - approx $3.01 effective per 1,000 comments at the free tier ($0.005 run-start + $0.003/comment x 1,000) - the highest effective cost of the actors checked, despite a low headline per-comment rate
- Cap on comments per video - none stated; `maxCommentsPerVideo` settable as high as needed, with a warning that very large runs may need longer timeouts
- Replies - yes, marked with `isReply: true` and `parentCommentId` to reconstruct threads
- Output fields - 16 fields including text, ids, likes, replies, timestamps, author details, profile URLs, avatars, video context
- Login/cookies needed - no
- Last modified - UNVERIFIED
- Users - 220 total, 17 monthly (low adoption)
- Success rate - 100.0% (small sample size caveat - very few total runs relative to the Clockworks actors)
Source - https://apify.com/automation-lab/tiktok-comments-scraper (read 2026-09-11)

### Others noted in the Store search for "tiktok comments" but not deep-checked
alien_force/tiktok-scraper-with-comments (listed at $1.00/1,000 comments, top-level comments only per the listing text, reply completeness UNVERIFIED), craig337/tiktok-comments-scraper, epctex/tiktok-comment-scraper - these appeared in the Store search results but were not individually fetched for full field/pricing verification in this pass; treat their specs as UNVERIFIED until checked directly.

## 3. Getting "the 20 most-commented videos on a profile"

Short answer - partially, with an important caveat: **there is no native "sort by comment count" option on any Apify TikTok actor checked, because TikTok's own public profile feed does not expose that sort either.**

clockworks/tiktok-profile-scraper's input schema has a `profileSorting` parameter with three options - "Latest," "Oldest," and "Popular." "Popular" sorts by heart/like count (`diggCount`), not by comment count, and per the listing is limited to roughly the most recent 400-500 videos per profile. There are also `mostDiggs`/`leastDiggs` threshold filters, again keyed to likes, not comments.
Source - https://apify.com/clockworks/tiktok-profile-scraper/input-schema (read 2026-09-11)

However, every video record the profile scraper returns does include a `commentCount` field. So the practical path is -

1. Run the profile scraper against each of the 5 accounts, pulling a reasonably large batch of each account's videos (e.g. "Latest" order, or "Popular"/most-liked as a rough proxy, capped at some N such as 100-200 videos per account since likes and comments are correlated but not identical).
2. Sort the returned records client-side (in a spreadsheet or a short script) by `commentCount` descending.
3. Take the top 20 per account and feed those 20 video URLs into the comments actor.

This is a genuine approximation of "top 20 most commented," not a guaranteed exact match, because a video outside your scraped sample window could theoretically have more comments than one inside it (most likely only relevant for prolific accounts with very long posting histories, where the true top-20-all-time videos might be old and buried past the "Latest" cutoff, or where "Popular"/likes-sort doesn't perfectly track comment volume). For accounts with a normal-sized back catalogue (roughly under a couple hundred videos), scraping the full catalogue removes this risk entirely.

## 4. Worked cost estimate

Assumptions: 5 accounts x 20 videos x up to 200 comments each = 20,000 comments. Using the cheapest verified actor that returns replies and needs no login.

**Cheapest by advertised list price** - apidojo/tiktok-comments-scraper at $0.30 per 1,000 comments.
- 20,000 comments / 1,000 = 20 units
- 20 x $0.30 = **$6.00**
- Caveat - this actor's own listing warns replies "may not always come through as expected," which matters given the brief needs a reliable is-reply flag.

**More reliable alternative** - clockworks/tiktok-comments-scraper at $0.50 per 1,000 comments (13x more total runs and users than apidojo, higher stated success rate, and a dedicated `maxRepliesPerComment` control rather than a single on/off toggle).
- 20 units x $0.50 = **$10.00**

**Profile-scrape cost to rank videos and find the top 20 per account** - using clockworks/tiktok-profile-scraper at $1.00 per 1,000 results. Assume scraping 100 videos per account as a representative sample to sort by `commentCount` (200 per account if the team wants higher confidence of catching the true top 20 on prolific accounts).
- 5 accounts x 100 videos = 500 results / 1,000 = 0.5 units x $1.00 = **$0.50**
- At 200 videos per account for higher confidence - 5 x 200 = 1,000 results = **$1.00**

**Total worked estimate**
- Cheapest path (apidojo comments + light profile sample) - $6.00 + $0.50 = **$6.50**
- More reliable path (Clockworks comments + fuller profile sample) - $10.00 + $1.00 = **$11.00**

Both totals sit above Apify's free-plan monthly credit ($5.00), so a paid Apify plan or a credit top-up would be needed to run this even once; on a paid plan the "Actor start" and platform-usage components of pay-per-event pricing (seen in the raw Apify API metadata for these actors, roughly $0.001-$0.006 per run start plus per-item charges) would add a small, likely-under-a-dollar amount on top of the above per batch of 5 accounts, which was not itemized above because the store-page headline prices already bundle this into the standard per-1,000 rate quoted.

## 5. TikTok's Terms of Service on automated collection / scraping

Quoted verbatim, from Section 3.4 ("What you can't do on the Platform") of TikTok's Terms of Service -

"scrape, crawl, export or otherwise extract any data or content in any form, for any purpose, from the Platform using any automated system or software, including automated 'bots,' except as approved in writing by TikTok USDS Joint Venture"

Source - https://www.tiktok.com/legal/page/us/terms-of-service/en (read 2026-09-11)

This is a broad, blanket prohibition covering any automated extraction "in any form, for any purpose," which on its face covers exactly the kind of Apify-actor-based collection described in sections 2-4 above, whether aimed at the team's own account or competitors' accounts. It is a contractual (Terms of Service) restriction, not a technical barrier by itself, and TikTok separately maintains technical countermeasures (its robots.txt broadly disallows automated crawlers, and it can rate-limit, IP-block, or suspend accounts associated with violations). Whether the ToS is enforceable against a party that never logged into or agreed to the platform (i.e., scraping while logged out) is a genuinely unsettled legal question region-to-region and was outside the scope of this research to resolve; this report only confirms what the ToS text says, not its enforceability.

## What was not verified

- Exact "last modified" / last-code-change dates for every Apify actor listed (the Apify API returned today's date for all of them, which reads as a metadata artifact rather than a genuine code-change date - flagged UNVERIFIED throughout).
- Full field lists, exact pricing, and reply-completeness for alien_force/tiktok-scraper-with-comments, craig337/tiktok-comments-scraper, and epctex/tiktok-comment-scraper - these appeared in Store search results but were not individually fetched.
- Whether TikTok's Terms of Service is legally enforceable against logged-out/anonymous scraping in Australia specifically - noted as an open legal question, not resolved here.
- The precise current per-item "Actor start" and platform-usage add-on charges across every subscription tier for each actor (the headline per-1,000 prices quoted are the store-page list prices; a live Apify console run would show the plan-specific breakdown).
