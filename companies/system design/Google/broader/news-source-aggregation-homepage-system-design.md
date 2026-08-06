# System Design: News-Source Aggregation Homepage

> **Focus areas:** Publisher ingest · Story clustering · Ranking · Personalization · Freshness · Paywall hooks · Homepage materialization  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (ingest docs/s, homepage QPS, cluster fan-in), split ingest/index/rank/serve planes, deal-breakers for “personalize by scanning all articles per request”  
> **Interview theme:** Google L5+ news aggregation — DB/index choice, partitioning by time/topic/user, ambiguity over Google internals (not Magenta/Monarch trivia)

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—a **news aggregation homepage** (Google News–class): ingest articles from many publishers, **cluster** duplicates into stories, **rank** a homepage with freshness + personalization + authority, and honor **paywall/licensing hooks** without becoming a full publisher CMS or TikTok-style short-video feed (sibling doc exists).

### 1.0 What this is / is not

| Dimension | **News aggregation homepage (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Ingest → cluster → rank → serve homepage | Publisher CMS / blogging platform |
| Success | Fresh, diverse, trustworthy, relevant | Max watch-time only |
| UX | Homepage sections + topic pages + story clusters | Vertical swipe Shorts-first |
| Personalization | Interests + locale + history | Full social graph fanout |
| Monetization | Paywall/affiliate/licensing hooks | Full ads auction deep dive |
| Correctness | Cluster quality + misinfo demotion | Perfect truth oracle |

**Scope statement:** Design a news-source aggregation homepage: publisher ingest, story clustering, multi-objective ranking, personalization, freshness, and paywall hooks—at progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Sources? | RSS/Atom, partner APIs, crawl sitemap | Ingest connectors + parsers |
| F2 | Homepage? | Top stories, For You, topics, local | Multiple shelves / modules |
| F3 | Clustering? | Same event → one story, many sources | Near-dup + entity clustering |
| F4 | Ranking? | Freshness × authority × relevance × diversity | Retrieval → rank → re-rank |
| F5 | Personalization? | Topics, location, language, history | Profile + realtime session |
| F6 | Freshness? | Breaking news minutes | Priority ingest + breaking channel |
| F7 | Paywall? | Show snippet; deep link to publisher; entitlements | Don’t host full paid body MVP |
| F8 | Local news? | Geo modules | Geo index |
| F9 | Safety? | Misinfo/medical/election policy | Classifiers + demote/drop |
| F10 | Notifications? | Breaking optional Phase 1.5 | Separate ranker |
| F11 | Publisher portal? | Claim/verify Phase 1.5 | Control plane |
| F12 | Multilingual? | Yes major langs | Lang detect + per-locale homepages |

**MVP functional scope:**

1. **Ingest** articles from publishers (RSS + partner feed) with dedup by URL canonical.  
2. Parse title/body/snippet/byline/time/lang; store durable docs.  
3. **Cluster** into stories (same news event).  
4. Build **homepage** modules: Top stories (edition), For You, Topics, Local.  
5. **Rank** with freshness, publisher authority, personalization, diversity, safety.  
6. **Serve** homepage JSON fast (materialized + light personalize).  
7. Clickthrough to publisher; **paywall hooks** (snippet-only, meter headers).  
8. Feedback: click, dismiss, subscribe interest, hide source.  
9. Admin: suppress story/source.

**Out of MVP:**

- Full-text host of all paywalled content  
- TikTok-style vertical video news (sibling)  
- Perfect global election integrity platform  
- Publisher CMS / analytics suite  
- Real-time collaborative comments graph  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest durability | No silent drop after ACK | Kafka + multi-AZ store |
| N2 | Breaking freshness | Fast surface | Ingest→homepage p99 < 1–5 min hot |
| N3 | Homepage latency | Instant | p99 < 100–200ms |
| N4 | Availability | Critical news moments | 99.9%+; stale-if-error OK |
| N5 | Personalization cost | Bounded CPU per request | Candidate ≤ few thousand |
| N6 | Publisher fairness | Diversity caps | Re-rank constraints |
| N7 | Safety | Policy demotions | Never “engagement only” |
| N8 | Multi-region | Editions by country/lang | Geo cells + edition keys |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Reuters publishes → RSS poll/push → parse → cluster joins “Earthquake in X” → Top stories.  
2. User opens homepage → edition + personalized shelves → clicks → publisher site (paywall there).  
3. User follows “Climate” → For You boosts climate clusters.  
4. Local metro module shows nearby outlets.  
5. Editor suppresses hoax cluster → removed next materialize.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate syndicated wire | Canonical URL + cluster; show multiple sources under story |
| SEO title farm spam | Authority prior; quality classifier; demote |
| Breaking spike | Priority lane; delay heavy personalization |
| Stale RSS | Conditional GET; sitemap crawl backoff; freshness score ↓ |
| Paywalled fulltext missing | Snippet-only card; CTA subscribe/open |
| Cluster wrong merge | Editor split; user feedback; tighter thresholds |
| Election/medical claim | Higher evidence bar; panel / authoritative sources |
| Locale mismatch | Lang detect; don’t mix editions blindly |
| Source outage | Homepage from last good materialization |
| Clickbait headline | Satisfaction feedback demotes (dwell/back-click) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Publishers | 10K | 50K | 200K | 1M+ blogs careful |
| New articles/day | 5M | 50M | 500M | crawl-heavy |
| Peak ingest docs/s | 200 | 2K | 20K | 200K |
| Active clusters | 1M | 5M | 20M | — |
| Homepage QPS | 50K | 500K | 5M | 50M |
| Editions (country×lang) | 100 | 300 | 500+ | — |
| Personalized % | 70% | 80% | 90% | — |
| Ranker feature QPS | 100K | 1M | 10M | edge features |
| Feedback events/s | 100K | 1M | 10M | — |

**What each jump forces:**

- **10×:** Priority ingest; cluster sharding; homepage materialization + CDN; candidate retrieval.  
- **100×:** Edition cells; two-stage rank; feature store; paywall entitlement cache.  
- **1,000×:** Near-dup LSH fleets; hierarchical story graphs; edge personalization light; push breaking.

### 1.5 Etc. (Constraints & Assumptions)

- Prefer **linking out** to publishers for full article (legal/licensing).  
- “Google News” values: **authority, diversity, freshness**—not pure engagement.  
- Ambiguity: exact crawl stack less important than ingest→cluster→rank→serve clarity.

**Scope statement to repeat back:**

> Design a news aggregation homepage that ingests publisher feeds, clusters articles into stories, retrieves and ranks modules with freshness/personalization/authority/diversity/safety, materializes hot editions for low latency, and deep-links to publishers with paywall hooks—scaling via candidate generation rather than scoring the corpus per request.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Ingest** | New/updated docs | ~200/s peak | Kafka + parsers |
| **Cluster updates** | Assign story | ~200/s | Clustering jobs |
| **Index writes** | Search/serving docs | ~200/s | Index |
| **Homepage reads** | GET home | ~50K/s | Edge + forge |
| **Ranker** | Score candidates | ~0.5–2M scores/s | Rank fleet |
| **Feedback** | clicks/dwells | ~100K/s | Kafka |
| **Breaking push** | optional | spiky | Notify |

**Anti-pattern:** one QPS mixing RSS polls and homepage GETs.

### 2.2 Homepage cost

```text
Naïve: score all 5M docs/day for each user request → DEAL-BREAKER
Must: retrieve K candidates (e.g. 500–2000) → score → return ~20–50 cards

50K homepage QPS × 1000 candidates × 100 ns feature = careful budgeting
→ Materialize non-personalized Top Stories per edition at edge
→ Personalize For You with smaller candidate union
```

### 2.3 Clustering cost

```text
Each new article: compare to recent active stories (hours–days), not all history
Use: blocking keys (time window × entities × simhash band) then pairwise
5M docs/day ≈ 60/s avg; peak 200/s — fine with sharded blockers
```

### 2.4 Storage

```text
5M docs/day × 5 KB meta/snippet = 25 GB/day
Fulltext optional × 50 KB = 250 GB/day if stored
Retain hot 30–90d online; cold archive
Cluster records tiny vs docs
```

### 2.5 Personalization profile

```text
User interests vector ~1–10 KB
100M MAU × 5 KB = 500 GB — fits profile store
Realtime session features in Redis
```

### 2.6 Paywall hooks

```text
Don’t mirror paid HTML at ingest scale without license
Store: snippet, lead image URL, canonical URL, paywall flag, product SKUs hooks
Entitlement check only if product includes subscriber browse of fulltext (usually out)
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/homepage?edition=` | Modules + cards (signed-in optional) |
| `GET /v1/stories/{id}` | Cluster page: sources timeline |
| `GET /v1/topics/{slug}` | Topic feed |
| `GET /v1/local` | Geo news |
| `POST /v1/feedback` | click, dismiss, hide_source, follow_topic |
| `POST /internal/ingest` | Push from partners (else pull workers) |
| `POST /admin/suppress` | Story/source suppress |

**Card schema (serve):**

```text
Card {
  story_id, title, snippet, image,
  sources: [{publisher, url, paywall: bool}],
  published_at, topics[], score_debug?
}
```

### 3.2 Data model

| Entity | Key | Store | Notes |
|--------|-----|-------|-------|
| Publisher | `pub_id` | SQL | authority, domain, license |
| Article | `doc_id` | Bigtable/SQL+obj | urls, times, lang, bodyref |
| StoryCluster | `story_id` | SQL | exemplar, centroid, times |
| Membership | `(story_id, doc_id)` | SQL | |
| Topic | `topic_id` | SQL | taxonomy |
| UserProfile | `user_id` | KV/SQL | interests, follows, hides |
| EditionHome | `(edition, shelf, ver)` | Redis/CDN | materialized |
| FeedbackEvent | append | Kafka | training |
| Policy | lists | SQL | suppress |

### 3.3 Ingest — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Crawl web only | Coverage | Cost/robots/noise | Supplement |
| **RSS/partner first** | Structured; polite | Miss some | **MVP** |
| Headless render all | JS sites | Expensive | Selective |
| User submit | — | Spam | Minor |

**Chosen:** Pull RSS + partner push; selective crawl; canonical URL dedup.

### 3.4 Clustering — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Exact title match | Simple | Misses rewrite |
| **Simhash / MinHash LSH** | Scale near-dup | Semantic misses |
| **Embedding + entity blocking** | Semantic stories | Cost |
| Single-linkage forever | — | Giant messy clusters |

**Chosen:** Time-decayed blocking + simhash near-dup + embedding similarity + entity overlap; periodic split/merge.

### 3.5 Ranking / personalization — Why X over Y

| Approach | Pros | Cons | Deal-breaker? |
|----------|------|------|---------------|
| Chronological only | Fresh | Poor relevance | Weak product |
| Pure engagement ML | Clicks | Clickbait/misinfo | **Yes alone** |
| **Multi-objective** | Trustworthy | Tuning | **Chosen** |
| Score full corpus / req | — | Impossible | **Yes** |

**Pipeline:** multi-retriever candidates → LTR score → re-rank (diversity, source caps, safety, paywall UX).

### 3.6 Homepage materialization — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Fully dynamic every request | Fresh personal | Cost/latency |
| **Hybrid: materialize global shelves + personalize For You** | Scale | Complexity |
| Fully precompute per user | Fast | Memory; stale |

**Chosen hybrid.**

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Corpus scan per request | Never | Cost | Score-all-docs |
| Clustering | LSH + embeddings + entities | Story UX | One card per URL only |
| Ranking | Multi-objective | Trust | Engagement-only |
| Serve | Materialize + light personalize | Latency | Heavy ML inline uncached |
| Content host | Snippet + deep link | Legal | Pirate fulltext mirror |
| DB | SQL meta + doc store + Kafka | Roles | One Mongo holding everything naïve |

**DB choice note:**  
- **Kafka:** ingest & feedback.  
- **Doc store (Bigtable/object):** article bodies/snippets.  
- **Search/inverted + ANN:** retrieval.  
- **Redis/CDN:** edition shelves.  
- **Feature store / online KV:** user profiles, publisher priors.  
- **Distributed SQL:** publishers, admin, cluster records.

---

## 4. Architecture Diagram

```text
 Publishers (RSS/API)
        |
        v
 +--------------+     +----------------+
 | Ingest Pull/ | --> | Kafka docs.raw |
 | Push Workers |     +--------+-------+
 +--------------+              |
                               v
                      +--------+-------+
                      | Parse/Clean/   |
                      | Canonicalize   |
                      +--------+-------+
                               |
               +---------------+---------------+
               v                               v
      +----------------+              +----------------+
      | Cluster Service|              | Doc Index      |
      | LSH+embed+ent  |              | (retrieval)    |
      +--------+-------+              +--------+-------+
               |                               |
               v                               v
      +----------------+              +----------------+
      | Story Store    |<------------>| Rank Features  |
      +--------+-------+              +--------+-------+
               |                               ^
               v                               |
      +----------------+      profiles        |
      | Homepage Forge |<----------------------+
      | materialize    |      User Profile Svc
      +--------+-------+
               |
               v
      +----------------+     +----------------+
      | Edge / CDN +   | --> | Homepage API   | --> Clients
      | personalize    |     | (light rerank) |
      +----------------+     +----------------+
               ^
               | feedback
        Clients --> Kafka feedback --> trainers / online learning
```

**Breaking path:**

```text
high-priority partner alert / sudden velocity
  -> priority cluster
  -> patch Top Stories materialization immediately
  -> optional push notify
```

**Homepage GET:**

```text
edition = geo/lang/user pref
fetch materialized Top/Local/Topic shelves (CDN)
if signed in:
  retrieve For You candidates (interest + collab + breaking)
  rank + re-rank constraints
  stitch modules
return JSON
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Ingest at-least-once**; idempotent on canonical URL / `doc_id`.  
2. **Suppress/policy wins** over engagement score.  
3. **Homepage always serves** last-good edition if forge lags (stale-if-error).  
4. **Cluster assignment durable**; splits/merges versioned.  
5. **Deep links** preserve publisher URL; don’t swap affiliate silently without disclosure policy.  
6. **Feedback ≠ ranking alone** without safety features.

#### 5.1.2 Ingest failure modes

| Failure | Mitigation |
|---------|------------|
| RSS 500 | Backoff; use last items; alert |
| Malformed XML | Dead-letter; quarantine publisher |
| Clock wrong published_at | Cap future dates; trust fetch time secondary |
| Duplicate URLs variants | Canonicalization rules (strip tracking params) |

#### 5.1.3 Cluster quality controls

- Thresholds + human/editor tools for split/merge.  
- Don’t merge across languages unless explicit.  
- Velocity spikes trigger review for medical/election topics.

#### 5.1.4 Ranking safety reliability

```text
hard_drop: CSAM, malware, legally blocked
soft_demote: low authority medical claims, known spam
source_cap: max N cards per publisher per homepage
diversity: topic/entity coverage constraints
```

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Parser bugs | Quarantine |
| 10× | Cluster hotspot | Shard by time×lang |
| 100× | Ranker overload | Materialize more; smaller K |
| 1,000× | Ingest flood | Admission; quality gate before cluster |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| Time buckets | Hot cluster search space |
| `lang` + edition | Serving isolation |
| `story_id` hash | Cluster storage |
| `user_id` | Profile shards |
| Publisher domain | Ingest scheduling |

#### 5.2.2 Candidate generation (critical)

| Retriever | Signal |
|-----------|--------|
| Breaking / fresh | Recency velocity |
| Top edition | Global authority rank |
| Topic follow | Interest match |
| Local | Geo proximity + local pubs |
| Collaborative | Users like you |
| Explore | Diversity / cold topics |

Union → dedupe by `story_id` → score.

#### 5.2.3 Scoring (MVP)

```text
score = w1*fresh + w2*authority + w3*personal + w4*quality - w5*spam
fresh = exp(-age / half_life) × velocity_boost
personal = dot(user_interests, story_topics) + history
re-rank: MMR diversity + publisher caps + safety
```

LTR model Phase 1.5 replaces linear weights with same features.

#### 5.2.4 Materialization

```text
every T seconds per edition:
  compute Top Stories shelf (non-personalized)
  compute Topic shelves head
  write versioned JSON to Redis + CDN
For You computed online from cached features
```

#### 5.2.5 Paywall hooks at scale

| Hook | Implementation |
|------|----------------|
| `paywall: true` flag | From publisher feed / heuristics |
| Snippet length policy | Store only allowed snippet |
| Open URL | Canonical with analytics redirect optional |
| Subscriber browse | Entitlement service if product includes |
| Amp/lite | Optional alternate URL field |

**Deal-breaker:** scraping and hosting full paywalled body as the core design without rights.

#### 5.2.6 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | LSH cluster; materialize editions; multi-retriever |
| →100× | Edition cells; LTR; feature store; source quality ML |
| →1,000× | Hierarchical stories; edge personalize; ingest admission |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
editions: [en-US, en-GB, zh-CN, ...]
half_life_minutes: {breaking: 30, standard: 360}
retriever_k: {fresh: 200, topic: 200, local: 100, collab: 200}
rerank:
  max_per_publisher: 2
  mmr_lambda: 0.7
cluster:
  simhash_threshold: 0.85
  embed_threshold: 0.82
  window_hours: 72
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `ingest_lag` | Freshness |
| `cluster_merge_rate` / split | Quality |
| `homepage_p99` | UX |
| `forge_publish_age` | Staleness |
| `ctr` / `satisfaction` | Ranking |
| `source_entropy` | Diversity |
| `suppress_hits` | Policy |
| `paywall_click_through` | Publisher value |

#### 5.3.3 Testing

- Golden clusters (wire duplicates → one story).  
- Ranking diversity unit tests (caps).  
- Chaos: forge down → CDN stale serve.  
- Spam publisher injection demoted.  
- Personalization doesn’t bury breaking for followed disasters (policy tests).

#### 5.3.4 Operability

- Shadow ranker `vNext`.  
- Edition canary.  
- Feature flag half-lives during elections.  
- Publisher authority admin tools.

#### 5.3.5 Feedback loop

```text
click, dwell, back-click, dismiss, hide_source, follow
→ Kafka
→ offline training daily + nearline feature adjust
careful: clickbait traps; use satisfaction proxies
```

---

## 6. Wrap-Up

### 6.1 What we designed

A **news aggregation homepage**: publisher ingest, **story clustering**, multi-retriever **ranking** with freshness/personalization/authority/diversity/safety, **hybrid materialization** for speed, and **paywall-aware deep links**—not a fulltext pirate mirror and not score-the-corpus-per-request.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Score all articles / request | Deal-breaker |
| Engagement-only rank | Deal-breaker |
| Host paywalled fulltext | Out / legal |
| Cluster stories | Required UX |
| Hybrid materialize | Scale serve |
| Breaking lane | Separate priority |

### 6.3 30-second scale narrative

> Baseline: RSS ingest → Kafka → cluster → index; materialize edition Top Stories; For You from small candidate union. 10× adds LSH and CDN shelves. 100× edition cells + LTR + feature store. 1,000× hierarchical stories and edge light-personalize—freshness from priority ingest, trust from multi-objective re-rank.

### 6.4 Deal-breakers checklist

- Personalization by scanning the entire article corpus online.  
- Ranking solely by clicks/CTR.  
- No clustering (100 near-identical cards).  
- Serving empty homepage when forge lags (should stale-if-error).  
- Building the product by republishing paywalled fulltext without rights.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Homepage vs search?**  
A: Homepage is curated modules; search is query-driven — share index, different rank.

**Q2: Host full article?**  
A: Prefer snippets + outbound links; licensing dependent.

**Q3: How local is local?**  
A: Metro/DMA from IP/profile; user-set home.

**Q4: User-generated news?**  
A: Out of MVP; spam risk.

**Q5: Video/podcast?**  
A: Cards can link; media CDN sibling.

### 7.2 Ingest

**Q6: Pull vs push?**  
A: Both; push for partners breaking; pull RSS widely.

**Q7: Canonical URL?**  
A: Strip tracking params; prefer `rel=canonical`; https normalize.

**Q8: How often to poll?**  
A: Adaptive by publisher velocity; conditional GET.

**Q9: Paywalled feeds?**  
A: May include only titles/snippets; respect robots/terms.

**Q10: Language detection?**  
A: On ingest; drives edition eligibility.

### 7.3 Clustering

**Q11: Article vs story?**  
A: Article = doc; story = cluster of coverage of same event.

**Q12: Simhash role?**  
A: Near-dup cheap filter before heavy embed.

**Q13: Why time window?**  
A: Same entities months apart ≠ same story.

**Q14: Multi-source layout?**  
A: Story page lists publishers; homepage shows exemplar + “+N sources”.

**Q15: Split/merge ops?**  
A: Version cluster ids; redirect old ids.

### 7.4 Ranking & personalization

**Q16: Cold start user?**  
A: Edition top + local + explore; short interest onboarding.

**Q17: Filter bubble?**  
A: Explicit diversity/explore quota in re-rank.

**Q18: Freshness vs relevance?**  
A: Multi-objective; breaking channel bypasses some personalization.

**Q19: Authority features?**  
A: Domain prior, expert graph, fact-check history, traffic quality — not PageRank trivia alone.

**Q20: Session personalization?**  
A: Mid-session topic stickiness + fatigue penalties.

**Q21: Why re-rank stage?**  
A: Easy to enforce constraints ML score alone misses (caps, diversity).

### 7.5 Serving

**Q22: Why materialize Top Stories?**  
A: Same for millions; CDN absorbs QPS.

**Q23: Cache personalization?**  
A: Short TTL per user segment; not forever.

**Q24: Stale-if-error?**  
A: Better old news than error page during forge outage.

**Q25: SSR vs JSON API?**  
A: Either; API+client fine for interview.

### 7.6 Paywall & publisher value

**Q26: How not to destroy publishers?**  
A: Deep link; limited snippet; prominent source; subscription paths.

**Q27: Metering?**  
A: Publisher-side; aggregator may pass logged-in hints carefully.

**Q28: Licensing tiers?**  
A: Some partners allow fuller preview — store rights flags.

**Q29: Scraping fulltext “for ML”?**  
A: Legal/policy sensitive — don’t assume allowed.

### 7.7 Safety & integrity

**Q30: Misinfo?**  
A: Classifiers + authoritative source boosting + demote unvetted claims on YMYL.

**Q31: Coordinated inauthentic?**  
A: Publisher quality, sudden network of domains, link graphs.

**Q32: Election mode?**  
A: Stricter ranking config; more human review hooks.

**Q33: Violence/graphic?**  
A: Label or filter per locale policy.

### 7.8 Data stores & partitioning

**Q34: Where is homepage JSON?**  
A: Redis/Memorystore + CDN by edition.

**Q35: Doc body store?**  
A: Object/Bigtable; index holds fields needed for retrieve.

**Q36: Feature store?**  
A: Online KV for publisher_authority, user_interests, story_velocity.

**Q37: Why not one Elasticsearch for everything?**  
A: Can do retrieval; still need cluster, materialize, constraints, profiles.

**Q38: Shard clusters how?**  
A: Hot window by time×lang; archive cold.

### 7.9 Estimation drills

**Q39: 5M QPS homepage scoring 1M docs each?**  
A: Impossible — show candidate math.

**Q40: Materialize 300 editions × 5 shelves / 10s?**  
A: 150 writes/s — trivial vs read QPS.

**Q41: Ingest 20K docs/s peak — Kafka OK?**  
A: Yes; parsers/cluster become bottleneck → scale consumers.

### 7.10 Alternatives & deal-breakers

**Q42: Only chronological RSS mashup?**  
A: Fails relevance, spam, duplicates.

**Q43: Only ChatGPT summarizer homepage?**  
A: Hallucination/rights issues; can be assist not core ingest.

**Q44: Social likes as sole rank?**  
A: Gaming/misinfo — deal-breaker alone.

### 7.11 Interview craft

**Q45: How to open?**  
A: Ingest sources, cluster, homepage modules, personalize, paywall, freshness SLO.

**Q46: What impresses L5+?**  
A: Candidate gen vs corpus scan, multi-objective re-rank, materialize hybrid, cluster blocking, policy wins.

**Q47: Common mistake?**  
A: Designing only ML model; ignoring ingest freshness and duplicate storms.

**Q48: Related sibling?**  
A: TikTok-style Google News vertical feed — different UX, shared ingest/cluster.

---

### Appendix A — Canonicalization rules

```text
1. Lowercase host; https preferred
2. Strip utm_*, fbclid, gclid
3. Respect rel=canonical if same domain
4. Remove mobile. m. prefixes carefully
5. Trailing slash normalize
```

### Appendix B — Cluster assign pseudocode

```text
onArticle(doc):
  blocks = blockers(time_window, lang, entities(doc), simhash_bands(doc))
  candidates = lookup(blocks)
  best = max sim(doc, cand)
  if best.score >= T: assign(best.story)
  else: new Story(doc)
  update story exemplar / velocity
```

### Appendix C — Homepage module stitch

```text
modules = []
modules << materialized["top"]
modules << personalized_for_you(user, k=10)
modules << materialized["local"]
modules << topic_shelves(user.follows)
apply_global_caps(modules)
return modules
```

### Appendix D — Re-rank constraints

```text
MMR select next card maximizing λ*score - (1-λ)*max_sim(selected)
enforce count(publisher) <= max_per_publisher
enforce safety demotions
optional: max_paywall_fraction
```

### Appendix E — Breaking velocity

```text
velocity = docs_in_cluster(last_15m) / baseline
if velocity > Z and authority_ok: boost breaking shelf
```

### Appendix F — Feedback event

```json
{
  "user_id": "u",
  "story_id": "s",
  "doc_id": "d",
  "type": "click|dismiss|hide_source|dwell",
  "dwell_ms": 4000,
  "ts": "..."
}
```

### Appendix G — Progressive scale table

| Scale | Ingest | Cluster | Rank | Serve |
|-------|--------|---------|------|-------|
| Baseline | RSS | Simhash | Linear | Redis home |
| 10× | Priority | LSH shards | Multi-retriever | CDN editions |
| 100× | Cells | Embed+entity | LTR+features | Hybrid FYP |
| 1,000× | Admission | Hier stories | Edge light | Push breaking |

### Appendix H — NFR card

```text
Breaking < 5m ingest→shelf
Homepage p99 < 200ms
Candidates bounded
Policy > engagement
Stale-if-error homepage
Snippet + deep link paywall
```

### Appendix I — Publisher authority prior

| Signal | Direction |
|--------|-----------|
| Domain age / stability | + |
| Correction rate | careful |
| Expert citations | + |
| Spam reports | − |
| Manual tier | override |

### Appendix J — Edition key

```text
edition = (country, lang, optional_region)
example: en-US, en-US-CA-SF, fr-FR
```

### Appendix K — Paywall card UX

```text
title + snippet (policy length)
badge "Subscription may be required"
primary CTA: Open at publisher
secondary: Follow topic / More sources
```

### Appendix L — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Elasticsearch with sort=date” | Dupes/spam/no personalization |
| “Personalize with full scan” | Math deal-breaker |
| “Host all articles” | Rights/cost |

### Appendix M — Related systems

| System | Role |
|--------|------|
| Kafka | Ingest/feedback |
| Bigtable/object | Docs |
| ANN/LSH | Cluster/retrieve |
| Redis/CDN | Shelves |
| Feature KV | Profiles/priors |
| SQL | Admin/publishers |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| Edition | Locale homepage variant |
| Story cluster | Group of articles on one event |
| Exemplar | Representative article/title for card |
| Retriever | Candidate source channel |
| MMR | Diversity-aware selection |
| YMYL | Your Money Your Life topics |

### Appendix O — Worked example

```text
Homepage 50K QPS
80% CDN hit on materialized Top = 40K served edge
20% need For You: 10K QPS × 800 candidates scored
= 8M score/s — with 50µs/score need ~400 cores order (features prejoined)
Argue feature precompute + smaller K + segment cache
```

### Appendix P — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Global same homepage? | No — editions + personal |
| Cluster eventual? | Yes shortly after ingest |
| Suppress latency | Next forge ≤ T seconds |
| Click feedback in rank | Nearline / next sessions |

### Appendix Q — 30m interview checklist

1. Clarify ingest, cluster, modules, personalize, paywall, freshness.  
2. Reject corpus-per-request scoring.  
3. Diagram ingest→cluster→forge→edge.  
4. Multi-objective re-rank + safety.  
5. Hybrid materialization math.  
6. Scale jumps.  
7. Deal-breakers.

### Appendix R — Topic taxonomy

```text
top-level: World, Business, Tech, Sports, Entertainment, Health, Science, Local
user follows subset; stories multi-label
```

### Appendix S — Hide source

```text
profile.hidden_publishers += pub_id
retrievers filter membership
story may still appear via other sources; demote that publisher's card
```

### Appendix T — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | LSH, CDN shelves, multi-retriever |
| 100× | LTR, feature store, edition cells |
| 1,000× | Hier clusters, edge FYP, ingest admission |

### Appendix U — Comparison vs TikTok-style news sibling

| | This homepage | Vertical Shorts-style |
|---|---------------|----------------------|
| UX | Shelves / story clusters | Swipe video/cards |
| Rank | Fresh×authority×personal | Session watch-time heavy |
| Media | Images + outbound | In-app video CDN |
| Shared | Ingest, cluster, safety | Same foundations |

### Appendix V — Admin suppress

```text
suppress(story_id or pub_id, reason, ttl?)
forge and online rank check policy store first
audit log immutable
```

---

*End of News-Source Aggregation Homepage system design.*
