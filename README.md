# Jypra SEO Agent — n8n + SearXNG + Replicate

A self-hosted agent that **measures** where `jypragroup.com.au` ranks on Google for your
72 target keywords, **generates on-page SEO content briefs** for the priority keywords that
aren't ranking yet, and **emails a daily report** to your lead. Built on n8n, with SearXNG
as a free search backend (no SERP API, no API key) and Replicate for the content model.

---

## Read this first — what an agent can and can't do

No automation makes a site rank on page 1–2 of Google. Ranking is *earned* through content
quality, technical SEO, internal linking, and — the big one for you — **domain authority and
backlinks**, which take months. Your own data shows why: `jypragroup.com.au` sits at authority
score **5** with ~**0** organic traffic and ranks for only **6–7** keywords, while all six
competitors (authority 15–25) outrank you across the board.

So this agent does the parts automation genuinely does well, which is the engine room of any
real ranking improvement:

1. **Rank tracking** — checks your live Google position for each keyword and logs history.
   You can't improve what you don't measure.
2. **Content briefs** — for the priority keywords (Quick Win / Commercial) where you're not
   yet on page 1–2, it drafts an SEO brief (H1, meta, outline, entities, internal links, intro)
   using a Replicate-hosted Llama model, mapped to the exact target page from your data.
3. **Reporting** — a daily email + two Google Sheets tabs (rank history, content briefs).

The part it can't do for you — earning backlinks, real expertise/E-E-A-T signals, and getting
the pages published — is where the actual ranking gains come from. Treat the briefs as the
first 30% of the work.

---

## Why SearXNG (and not a SERP API)

You asked for a free alternative to SERP API. As of June 2026 the landscape changed:

| Option | Free tier status |
|---|---|
| Bing Web Search API | **Retired** (~Aug 2025) |
| Brave Search API | Free tier **removed Feb 2026** → $5 credit/mo (~1,000 queries) |
| Google Custom Search JSON API | 100/day free but **closed to new sign-ups**, deprecating Jan 2027 |
| **SearXNG (self-hosted)** | **100% free, no key, no cap** — you run it |

SearXNG is an open-source metasearch engine you host yourself. It queries Google on your behalf
and returns clean JSON. For ~72 keywords once a day it's a tiny load. One honest caveat: it
*scrapes* upstream engines, so under heavy use it can get rate-limited/CAPTCHA'd, and the result
order is SearXNG's merge of Google's results (very close to Google's order, not byte-identical).
For low-volume internal rank tracking it's the right tool. The workflow throttles to 1 request
every 1.5s to stay well-behaved.

---

## Files

- `docker-compose.yml` — runs n8n + SearXNG (+ a cache) locally.
- `searxng-settings.patch.yml` — the one change needed to turn on SearXNG's JSON API.
- `n8n-seo-rank-tracker.json` — the importable workflow, pre-loaded with your 72 keywords.
- `keywords.json` — the extracted keyword dataset (for reference / re-import).

---

## Setup (about 20 minutes)

### 1. Start the stack
```bash
docker compose up -d
```

### 2. Enable SearXNG's JSON API
Edit `./searxng/settings.yml` (created on first start) and merge in the keys from
`searxng-settings.patch.yml`, then:
```bash
docker compose restart searxng
curl "http://localhost:8080/search?q=cyber+security+brisbane&format=json" | head
```
You should see a JSON `results` array.

### 3. Get a Replicate token
Sign up at replicate.com → Account → API tokens. Copy the `r8_...` token.
The workflow calls `meta/meta-llama-3-8b-instruct` with `Prefer: wait` (synchronous, no polling).
Swap the model in the **Replicate: Generate Brief** node URL if you prefer another text model.

### 4. Import the workflow
Open `http://localhost:5678` → **Workflows → Import from File** → `n8n-seo-rank-tracker.json`.

### 5. Wire up the three credentials (placeholders say `REPLACE_ME`)
- **Replicate** → on the *Replicate: Generate Brief* node, create an **Header Auth** credential:
  - Name: `Authorization`  Value: `Bearer r8_your_token_here`
- **Google Sheets** → create a *Google Sheets OAuth2* credential, then on both Sheets nodes
  set the `documentId` (your spreadsheet) and pick the tab (`RankLog`, `ContentBriefs`).
- **Gmail** → create a *Gmail OAuth2* credential and set the **Email Lead** node's `sendTo`
  to your lead's address. (Or swap this node for SMTP / Slack — your call.)

### 6. Test
Click **Test workflow**. It will: load keywords → query SearXNG (throttled) → parse positions
→ log to Sheets → email the summary → generate briefs for low-ranking priority keywords.
Once happy, toggle **Active** (it's scheduled for 6am Brisbane daily).

---

## How the workflow flows

```
Schedule (daily 6am)
  → Load Keywords (your 72, embedded)
  → SearXNG Search (1 req / 1.5s, engine=google, lang=en-AU)
  → Parse Rank (find jypragroup.com.au position, compute page, flag priority gaps)
       ├→ Append Rank Log        (Google Sheet, one row per keyword)
       ├→ Build Summary → Email Lead   (HTML report)
       └→ Needs Content Brief?  (Quick Win/Commercial AND not on pg 1–2)
              → Replicate: Generate Brief → Format Brief → Append Content Briefs
```

## Tuning notes
- **Positions beyond ~10–20:** SearXNG returns roughly the first page. To track deeper, add a
  second SearXNG node with `pageno=2` and merge — or accept "not in top results" as the signal
  to prioritise that page.
- **Replicate spend:** briefs only fire for priority keywords not on page 1–2, so a typical run
  is a handful of calls, not 72. Tighten/loosen the rule in the *Parse Rank* node (`needs_brief`).
- **Local-pack/maps keywords** (e.g. "cyber security brisbane") behave differently from organic;
  treat their positions as indicative.
- **Swap the data source:** replace the *Load Keywords* code node with a Google Sheets / CSV read
  if your SEO team wants to maintain the keyword list outside the workflow.
