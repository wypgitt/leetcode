# System Design: Find-Friends Service

> **Focus areas:** Contact upload · Phone/email hashing · Graph suggestions · Privacy · Rate limits · Social graph features (mutuals, PYMK)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct privacy threat model for address books, explicit hashing/matching design, deal-breakers for “upload plaintext contacts to shared DB and SELECT *” or “unbounded suggestion fanout without RL”  
> **Interview theme:** Amazon SDE III / L6 — design a **find-friends** service: upload contacts, match to users, suggest people-you-may-know, respect privacy & consent, rate-limit abuse—owned with trust, cost, and clear data minimization

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—help users **find friends** already on the platform via **contact upload / address-book matching**, **graph-based suggestions** (PYMK: people you may know), with strong **privacy**, **consent**, and **rate limits**, plus core **social graph features** (follow/friend edges, mutuals)—scaled 10×/100×/1,000×.

### 1.0 What this is / is not

| Dimension | **Find-friends service (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Match contacts + suggest likely friends | Full social network feed/media product |
| Success | High-precision suggestions; zero creepy leakage; hard to scrape | Perfect friend oracle / stalker toolkit |
| Data | Hashed contacts, edges, suggestion scores | Store raw address books forever in cleartext |
| Graph | Edges + mutual counts + PYMK | Full FB Groups / feed ranking |
| Privacy | Consent, minimization, anti-enumeration | “Growth at all costs” |
| Amazon lens | Customer trust, abuse, cost of graph compute | Only ML embedding trivia |

**Scope statement:** Design find-friends: contact upload/match, graph suggestions, privacy, rate limits, social graph features—progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Contact upload? | Yes — phone/email from address book | Client normalize + hash; server match |
| F2 | Match existing users? | Yes — show which contacts are on platform | Contact index by hash |
| F3 | Invite non-users? | Optional — send invite link/SMS carefully | Abuse controls; consent |
| F4 | PYMK suggestions? | Yes — friends-of-friends, mutuals, signals | Graph + ranking job |
| F5 | Friend/follow edges? | Yes — core graph | Graph service |
| F6 | Mutual friends count? | Yes | Efficient intersection / precompute |
| F7 | Block / ignore suggestion? | Yes | Negative signals |
| F8 | Privacy controls? | Who can find me by phone/email; contact sync on/off | Settings + index presence |
| F9 | Reverse lookup protection? | Don’t let attackers probe phones | Rate limit; hashed; uniform responses |
| F10 | Soft notifications? | “X joined from your contacts” opt-in | Careful privacy |
| F11 | Import Facebook/Google? | OAuth Phase 1.5 | Similar match pipeline |
| F12 | Ranked reasons? | “3 mutual friends” | Explainability |
| F13 | Bulk sync vs delta? | Delta after first full sync | Sync tokens |
| F14 | Multi-device? | Same user merges contact sets | Per-user contact store |
| F15 | Remove uploaded contacts? | Yes — user delete | Erasure pipeline |

**MVP functional scope:**

1. Opt-in contact sync: normalize → hash → upload → match.  
2. Return on-platform contacts (with privacy settings respected).  
3. PYMK suggestions from FoF / mutuals (+ light signals).  
4. Friend request / follow actions (thin) + block/ignore.  
5. Mutual friends count for suggestion cards.  
6. Privacy settings: discoverability by phone/email.  
7. Strict rate limits & anti-scraping.  
8. Delete/erase uploaded contacts.  
9. Metrics: match rate, suggestion CTR, abuse.

**Out of MVP:**

- Full feed / media social product  
- Global people search by name fuzzy at Google scale  
- Guaranteed SMS delivery product  
- Training giant GNN platform (hooks OK)  
- Storing raw phone numbers server-side long-term in cleartext

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Sync latency | Interactive first page | p99 < 1–2 s match return for typical book |
| N2 | Suggestion freshness | Daily OK; nearline better | Hours typical; minutes for edges |
| N3 | Privacy | Hard requirement | No unauthorized discoverability |
| N4 | Anti-enumeration | Hard | RL + detection; hashed identifiers |
| N5 | Availability | Growth feature important | 99.9% |
| N6 | Durability | Edges durable; contacts erasable | Graph durable; contacts deletable |
| N7 | Cost | Graph compute can explode | Cap FoF expansion; batch PYMK |
| N8 | Scalability | Progressive | 10×/100×/1,000× |
| N9 | Compliance | GDPR/CCPA delete | Documented erasure |
| N10 | Abuse | Invite spam, scraping | Quotas, reputation |
| N11 | Correctness | Matches precise on normalized forms | Canonicalization library |
| N12 | Operability | Clear ownership | Privacy SEV runbooks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User opts in → app uploads hashed contacts → service returns matches already registered → user sends friend requests.  
2. User opens Find Friends → sees PYMK ranked list with mutual counts and reasons.  
3. User ignores a suggestion → demoted permanently (or long cooldown).  
4. User disables “find me by phone” → removed from contact match index.  
5. User deletes synced contacts → server erases contact blobs/hashes for that user.  
6. Two users share many mutuals → high PYMK score both ways (asymmetric still OK).  
7. New user joins with phone → opt-in notify contacts who already synced that hash (if settings allow).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Shared family phone / landline | Multiple users claim; careful matching / verification |
| Hash collision (rare) | Use strong hash + HMAC; verify secondary signals |
| Attacker uploads millions of guessed phones | Hard rate limits; anomaly; CAPTCHA; ban |
| Contact book 50k entries | Cap upload; chunk; prioritize |
| Non-normalized numbers (+1 vs local) | E.164 canonicalization client+server |
| Email case / dots Gmail | Provider-aware normalize carefully |
| User not discoverable | Match API omits them (uniform) |
| Suggestion to blocked user | Never |
| FoF explosion (celebrity friend) | Cap expansion; exclude celebs as bridges optional |
| Stale suggestions after friend | Filter already-friends |
| Partial sync failure | Resume via sync token; idempotent upserts |
| Invite SMS to non-consenting | Strict quotas; templates; legal review |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 50M | 500M | cells | cells |
| Contact syncs / day | 5M | 50M | 500M | 5B |
| Avg contacts / sync | 500 | 500 | 500 | 500 |
| Contact hash upserts / day | 2.5B | 25B | 250B | — (delta+cap) |
| Match QPS peak | 10K | 100K | 1M | shard+edge |
| PYMK requests / day | 200M | 2B | 20B | cache-heavy |
| Graph edges | 10B | 100B | 1T | cell graph |
| Friend requests / day | 20M | 200M | 2B | RL enforced |
| Suggestion compute | daily batch | hourly | nearline | incremental |

**What each jump forces:**

- **10×:** HMAC contact index; chunked upload; Redis match cache; batch PYMK; strict RL.  
- **100×:** Shard contact index by hash prefix; sharded graph; incremental FoF; privacy settings cache.  
- **1,000×:** Cells; approx mutuals; embedding ANN optional; aggressive caps; dedicated abuse ML.

### 1.5 Etc. (Constraints & Assumptions)

| Assumption | Choice |
|------------|--------|
| Identifiers | Phone E.164 + email normalized |
| Server storage of contacts | **HMAC-SHA256** with server secret (or per-app pepper); not raw |
| Discoverability default | Opt-in match; conservative defaults |
| Graph | Directed follow or bi-di friends — support both edges |
| PYMK | FoF + mutual count + co-contact + co-interaction light |
| Invites | Optional, heavily rate-limited |
| ML | Ranking hook; rules first |

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Examples | Notes |
|-------|----------|-------|
| Contact sync writes | Upload hashes | Bursty; chunked; idempotent |
| Match reads | Hash → user_id | Hot index lookup |
| Graph writes | Friend/follow | Moderate |
| PYMK reads | Suggestion list | Cacheable per user hours |
| PYMK compute | FoF expansion | Offline/nearline heavy |
| Abuse | Scraping attempts | Must detect |

### 2.2 Contact storage math

```text
5M syncs/day × 500 contacts = 2.5B hash upserts/day (upper if full resync)
With delta sync 10% change → 250M upserts/day more realistic steady state

Per contact record ~64–128 B (hmac, type, metadata) 
250M × 100 B ≈ 25 GB/day churn metadata (plus index)

Contact index: global map hmac -> [user_ids who own this credential]
Also user -> set of hmacs uploaded (for erase / match display)
```

### 2.3 Match QPS

```text
First-time sync: 500 hashes matched via batch mget / multi-lookup
5M syncs/day ≈ 58/s average; peak 10× → ~600 syncs/s × 500 = 300K hash lookups/s
→ batching + Redis/Bloom + sharded KV mandatory at 10×+
```

### 2.4 PYMK compute math (must nail)

```text
Naive FoF: for user with 300 friends, each with 300 friends → 90K candidates
× 50M users daily recompute → insane

Strategies:
  - Cap friends considered (top interactive 50–100)
  - Exclude celebrities as bridges
  - Incremental: only recompute users near edge changes
  - Precompute mutual counts for candidate pairs sample
  - Limit candidates stored per user (e.g. 500–2000)
```

### 2.5 Latency budgets

| Path | Target |
|------|--------|
| Contact chunk match | < 200–400 ms / chunk |
| Full first sync UX | < 1–2 s to first results (parallel chunks) |
| PYMK read cached | < 100 ms |
| Friend request | < 200 ms |

### 2.6 Rate limit budgets (abuse)

```text
Match API: per-user daily hash lookup cap (e.g. 5k–20k)
Friend request: tens–hundreds / day
Invite SMS: very low (e.g. 5–20 / day)
New accounts: tighter
```

### 2.7 Scale jump worksheet

| Jump | Investment |
|------|------------|
| 10× | HMAC index, chunk sync, RL, batch PYMK |
| 100× | Hash-prefix shards, incremental PYMK, graph shards |
| 1,000× | Cells, approx mutuals, ANN, abuse ML |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Privacy & minimization first** — raw address books don’t land in cleartext logs.  
2. **Precise matching** via canonicalization + HMAC.  
3. **Suggestions useful but not creepy** — explainable mutuals; respect settings.  
4. **Hard to scrape** — rate limits, anomaly, uniform negative responses.  
5. **Graph features correct** — edges, mutuals, blocks.  
6. **Cost-bounded FoF** — caps and incremental compute.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Edge / API GW | Auth, RL, bot detection |
| Contact Sync Service | Accept chunks; validate; store user contact sets |
| Canonicalizer | E.164 / email normalize (shared lib client+server) |
| Contact Match Index | `hmac → user_ids` (discoverable only) |
| Graph Service | Edges, blocks, requests |
| Mutual / Intersection Service | Mutual counts |
| PYMK Generator | Batch/nearline candidate + score |
| PYMK Serving | Cached ranked lists |
| Privacy Settings Service | Discoverability flags |
| Invite Service (optional) | Tokenized invites; quotas |
| Erasure Worker | Delete contacts / index entries |
| Abuse / Anomaly | Scraping detection |
| Event Bus | `edge_changed`, `user_joined`, `settings_changed` |

### 3.3 Contact hashing design (say clearly)

```text
Client:
  1. Request sync permission (OS dialog)
  2. Normalize phone → E.164; email → lower/trim (policy)
  3. Optional: client pepper from server session
  4. Upload HMAC or raw over TLS for server-side HMAC

Server (preferred):
  hmac = HMAC_SHA256(server_secret, "phone:" + e164)
  store under user_id; upsert index if discoverable

Why HMAC not plain SHA256(phone)?
  - Rainbow tables on SHA256(phone) are feasible
  - Server secret (KMS) raises cost of offline attack if DB leaks
```

**Never log raw numbers.** Redact in analytics.

### 3.4 Privacy settings

| Setting | Effect |
|---------|--------|
| `find_me_by_phone` | Include/exclude phone hmac in match index |
| `find_me_by_email` | Same for email |
| `contact_sync_enabled` | Allow upload store |
| `notify_when_contact_joins` | Opt-in |
| `show_mutual_friends` | Card display |

Default: require explicit opt-in for sync; discoverability may default on with clear UX — **state your choice** (interview: often discoverability on for growth but sync opt-in).

### 3.5 API sketch

```text
POST /v1/contacts/sync
  body: { sync_token, contacts: [{kind, value_hmac or e164, name?}] }
  → { sync_token', matches: [{contact_ref, user_id, profile_stub}], stats }

DELETE /v1/contacts
  → erase uploaded contacts for user

GET /v1/friends/suggestions?cursor=
  → [{user_id, score, reasons: ["mutual:3"], mutual_count}]

POST /v1/friends/requests {to_user_id}
POST /v1/friends/requests/{id}/accept
POST /v1/friends/ignore {user_id}
POST /v1/users/{id}/block

GET /v1/users/{id}/mutual-friends?cursor=

GET /v1/settings/privacy
PATCH /v1/settings/privacy

POST /v1/invites  # optional, heavily limited
```

### 3.6 Data model

**UserContact:** `user_id`, `hmac`, `kind`, `last_seen_at`, `display_name_enc?` (optional, careful)

**MatchIndex:** `hmac` → sorted set / list of `user_id` with discoverability true

**Edge:** `from`, `to`, `type`, `state`

**Suggestion:** `user_id`, `candidate_id`, `score`, `reasons[]`, `computed_at`

**Ignore:** `user_id`, `candidate_id`, `until`

**PrivacySettings:** flags per user

### 3.7 Sync + match flow

1. Auth + RL + opt-in check.  
2. Canonicalize; compute HMAC.  
3. Upsert into `UserContact` store (chunked, idempotent).  
4. Batch lookup MatchIndex; filter self; filter blocked; filter non-discoverable.  
5. Return matches with minimal profile stub.  
6. Async: trigger PYMK refresh signal (low priority).

### 3.8 PYMK pipeline

**Signals (MVP):**

- Mutual friend count (strong)  
- FoF edges  
- Co-appear in each other’s contact match (symmetric contact)  
- Same school/work soft (optional)  
- Negative: ignore, block, declined request  

**Compute:**

```text
for users with edge deltas (nearline):
  candidates = expand_fof_capped(user)
  score = w1*mutuals + w2*co_contact + w3*affinity - penalties
  write top K to Suggestions store
Serving: read precomputed list; filter already connected; hydrate
```

### 3.9 Social graph features

| Feature | Design |
|---------|--------|
| Follow/friend | Graph service state machine |
| Mutual friends | Intersection of adjacency; cap listing |
| Common contacts | Intersection on hmac sets (careful privacy) |
| Block | Suppress match, suggest, request |
| Request | Pending inbox |

**Mutual count optimization:** precompute for suggestion pairs; for profile use sampled intersection or cached BiBFS limited.

### 3.10 Rate limits & anti-scrape

| Surface | Limit ideas |
|---------|-------------|
| Hashes / day / user | Hard cap |
| Sync calls / hour | Token bucket |
| Match miss ratio | Anomaly if too many misses (probing) |
| Friend requests | Daily cap |
| Mutual friends pagination | Slow |
| New account | Stricter; device reputation |

Uniform empty match results timing (constant-time-ish) to reduce oracles.

### 3.11 Tradeoffs table

| Decision | Choice | Why |
|----------|--------|-----|
| Raw vs HMAC storage | HMAC + KMS secret | Leak resistance |
| Online FoF vs batch PYMK | Batch/nearline | Cost |
| Exact mutuals | Exact for small; approx at huge | Scale |
| Invites | Optional tight RL | Abuse |
| Client hash only | Server HMAC preferred | Secret stays server |

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
 Mobile/Web --> Edge (auth, RL, bot score)
                   |
       +-----------+------------+--------------+
       v           v            v              v
 Contact Sync   Privacy     Graph Svc      PYMK Serve
       |        Settings        |              ^
       v           |            v              |
 Contact Store <---+      Edge Store     Suggestions KV
       |                            |
       v                            v
 Match Index (hmac->users)    Mutual/FoF workers
       ^                            ^
       |                            |
 Erasure <---- settings_changed / delete
       |
 Abuse Monitor (lookup patterns)
       |
 Event Bus: edge_changed --> PYMK incremental
```

### 4.2 Contact sync sequence

```text
Client -> Sync: POST chunk (normalized values)
Sync -> Canonicalize + HMAC
Sync -> Contact Store upsert
Sync -> Match Index mget
Sync -> filter privacy/block
Sync -> Client matches
Sync -> Bus: contacts_updated (async PYMK hint)
```

### 4.3 PYMK read sequence

```text
Client -> PYMK Serve: GET suggestions
Serve -> Suggestions KV: top list
Serve -> filter friends/pending/ignore/block
Serve -> hydrate profiles + mutual_count
Serve -> Client
```

### 4.4 Discoverability change

```text
User disables find_me_by_phone
Privacy -> remove user from Match Index for phone hmacs
-> optional notify erasure metrics
Match API immediately stops returning user
```

### 4.5 Sharding at 100×+

```text
Match Index shard = hash_prefix(hmac)
Graph shard = user_id
PYMK compute = queues by user_id ranges / cells
Cross-cell FoF: limited RPC budgets
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. Non-discoverable users never appear in match results.  
2. Blocked pairs never suggested.  
3. Deleted contacts eventually erased from store+index (SLO).  
4. Edge accept materializes correctly for mutuals.  
5. Rate limits enforced at edge independently of backend bugs.

#### 5.1.2 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Match index down | Sync degraded | Cached recent matches; fail soft |
| Graph down | No requests/mutuals | Fail closed social writes |
| PYMK stale | Old suggestions | Serve stale OK; recompute lag alert |
| KMS secret unavailable | Cannot HMAC new | Fail closed sync |
| Abuse false positive | Blocks legit sync | Appeals; graduated challenges |

#### 5.1.3 Durability & erasure

- Graph edges: durable multi-AZ.  
- Contacts: durable but **deletable**; define RPO for erase (e.g. 24h).  
- Suggestions: recomputable; low durability OK.  
- Backups of contact stores must respect erasure (crypto-shredding optional).

#### 5.1.4 Consistency

| Path | Model |
|------|-------|
| Match after settings off | Strong-ish via sync index delete |
| PYMK | Eventual hours |
| Mutual counts on card | Slightly stale OK |
| Friend request | Read-your-write on inbox |

#### 5.1.5 Security & privacy deep

- TLS everywhere; no raw phones in logs/metrics labels.  
- HMAC secret in KMS; rotate with dual-write rehash job.  
- Prevent oracle: don’t reveal “number exists but not discoverable” differently from “not exists” if possible.  
- Admin access audited.  
- Threat: law enforcement requests — legal process, not eng backdoor in design interview (mention compliance path).

### 5.2 Scalability

#### 5.2.1 Match index scaling

- Shard by `hmac` prefix.  
- Redis cache hot hmacs (celebrities’ phones? careful — still privacy).  
- Bloom filter “hmac might exist” to cut misses (optional; watch false oracle).  
- Batch APIs only (no single phone online probing API public).

#### 5.2.2 PYMK scaling

- Incremental triggers on `edge_changed`.  
- Cap expansion degree.  
- Celebrity exclusion from bridge set.  
- Store only top-K.  
- At 1,000×: embedding ANN as additional recall; still filter graph rules.

#### 5.2.3 Graph scaling

- Adjacency lists chunked.  
- Mutual intersection: for large degrees use sorted posting lists / roaring bitmaps / approx.  
- Shard by user; cross-shard mutual with budgets.

#### 5.2.4 Sync scaling

- Chunk 100–500 contacts/request.  
- Delta sync tokens (watermark).  
- Idempotent upserts.  
- Backpressure large books.

#### 5.2.5 Multi-region

- User home region for contact store.  
- Match index global or regional with replication (phones global).  
- PYMK compute regional.  
- Consider data residency for contact hashes (still personal data!).

#### 5.2.6 Cost controls

| Lever | Effect |
|-------|--------|
| Delta sync | Fewer writes |
| Cap FoF | CPU/graph $ |
| Top-K suggestions | Storage |
| Batch compute | Smooth load |
| RL | Abuse $ |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership

| Surface | Owner |
|---------|-------|
| Contact sync/match | Growth identity team |
| Privacy settings | Privacy platform |
| Graph | Graph team |
| PYMK | Recommendations |
| Abuse RL | Trust & safety eng |
| Erasure | Privacy eng + storage |

#### 5.3.2 Safe evolution

- Canonicalization library versioned (mismatches cause missed friends — dual-write old/new hashes during migrate).  
- HMAC rotation dual-index.  
- Suggestion schema additive reasons.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Sync chunk p99 | < 400 ms |
| Erasure complete | < 24 h |
| PYMK freshness p95 | < 24 h (tighter later) |
| Match privacy incidents | 0 |
| Abuse block effectiveness | tracked |

Metrics: upload size dist, match rate, suggestion CTR, ignore rate, probe suspicion score.

#### 5.3.4 Progressive scale checklist

| Scale | Checklist |
|-------|-----------|
| 10× | HMAC index, chunk sync, RL, batch PYMK, erase API |
| 100× | Sharded index/graph, incremental PYMK, anomaly |
| 1,000× | Cells, approx mutuals, ANN hook, residency |

### 5.4 Deep dive: canonicalization

```text
phone: parse with libphonenumber → E.164; drop non-mobile optional
email: trim, lower; optional Gmail dot-removal policy (document)
Never invent SMS for invalid
Store kind+hmac only
```

Mismatches between client/server libs → missed matches; run golden test suite.

### 5.5 Deep dive: anti-enumeration

Attacker goal: learn which phone numbers are registered.

Controls:

1. No public “isRegistered(phone)” API.  
2. Only via authenticated sync with uploaded book UX friction.  
3. Daily hash caps.  
4. Detect sequential/random high-entropy uploads.  
5. Device binding / phone verification of the account itself.  
6. Return matches only; don’t return negative existence bit separately.  
7. CAPTCHA / step-up on anomaly.

### 5.6 Deep dive: mutual friends

```text
function mutual_count(a, b):
  # assume adjacency cached as sorted IDs or bitmap
  return |friends(a) ∩ friends(b)|

function mutual_list(a, b, limit):
  intersect; filter privacy of those friends; return stub list
```

At large degree, compute async and cache on suggestion object.

### 5.7 Deep dive: erasure & crypto-shredding

Option A: delete rows by `user_id` from contact store; remove from inverted index postings.  
Option B: per-user encryption key; destroy key (crypto-shred) for faster backup compliance.  
Index postings still need explicit delete either way.

### 5.8 Deep dive: co-contact signal

If Alice uploaded hmac(X) and Bob’s account is X and Bob uploaded hmac(Alice), boost PYMK.  
Still respect discoverability. Don’t reveal raw contact names across users without care (show platform names only).

### 5.9 Testing & resilience

- Golden normalize tests per country.  
- Privacy property tests: settings × match matrix.  
- Load: 50k contact book chunked.  
- Red team: enumeration attempts.  
- PYMK offline eval: precision@K.

### 5.10 Amazon leadership connection

- **Customer Trust** > growth hacks that leak address books.  
- **Frugality:** capped FoF beats heroic clusters.  
- **Dive Deep:** HMAC vs SHA, oracle attacks.  
- **Ownership:** erasure SLO is paged.

---

## 6. Wrap-Up

### 6.1 30-second recap

Find-friends is a **privacy-preserving contact match index + graph suggestion system**: opt-in sync, canonicalize & HMAC contacts, match only discoverable users, serve PYMK from capped FoF/mutuals computed nearline, enforce aggressive rate limits against enumeration, and support graph primitives (requests, blocks, mutuals) with erasure and settings that actually work.

### 6.2 Key tradeoffs

| Tradeoff | Pick |
|----------|------|
| Growth vs privacy | Opt-in sync; settings honored |
| SHA vs HMAC | HMAC + KMS |
| Online FoF vs batch | Nearline/batch |
| Exact mutuals | Exact small; approx huge |
| Invites | Optional + tiny quotas |

### 6.3 Risks & follow-ups

- Canonicalization bugs → missed friends (growth metric).  
- HMAC rotation complexity.  
- Celebrity FoF explosion.  
- Legal residency of contact hashes.  
- False positive abuse locks.

### 6.4 What “good” looks like

- Threat model for address books explicit.  
- Match index design + privacy flags.  
- PYMK cost math.  
- Rate limits as first-class.  
- Erasure & ownership clear.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. Opt-in vs opt-out sync?  
2. Store contact display names?  
3. SMS invites in MVP?  
4. Email-only users without phone?  
5. Soft notify “contact joined”?  
6. Cross-app OAuth import?  
7. Suggestion reasons always shown?  
8. Max contacts per user?  
9. Kids/teens policy?  
10. Business accounts discoverability?  
11. Merge duplicate accounts same phone?  
12. Export my contacts data?

### 7.2 Privacy & hashing (Q13–Q28)

13. Why HMAC over SHA256?  
14. Secret rotation plan?  
15. Rainbow tables realistic?  
16. Client-side hashing pros/cons?  
17. Oracle via timing?  
18. Logs redaction strategy?  
19. Backup erasure?  
20. Lawful access process (high-level)?  
21. Shared phones?  
22. Default discoverability choice justify.  
23. Difference “no match” vs “hidden”.  
24. Co-contact creepiness.  
25. GDPR lawful basis.  
26. Third-party analytics leakage.  
27. Admin tool abuse.  
28. Photo contact sync?

### 7.3 Graph & PYMK (Q29–Q44)

29. FoF cap strategy.  
30. Celebrity bridge problem.  
31. Incremental vs daily full.  
32. Score features.  
33. Cold start new user.  
34. Ignore half-life.  
35. Mutual list privacy of third parties.  
36. Directed vs undirected edges.  
37. Embedding ANN integration point.  
38. A/B ranking.  
39. Diversity of suggestions.  
40. Graph partition for mutual.  
41. Request spam rings.  
42. Block propagation to PYMK.  
43. Recompute storm after celebrity accept?  
44. Cost per MAU of PYMK.

### 7.4 Rate limits & abuse (Q45–Q56)

45. Designing hash/day caps.  
46. Detecting sequential phone probes.  
47. Device reputation signals.  
48. CAPTCHA placement.  
49. Invite credit system.  
50. Fake account farms.  
51. Distributed upload via bots.  
52. Soft vs hard bans.  
53. Match API batching rules.  
54. Edge RL vs central RL store.  
55. New number / SIM swap accounts.  
56. Red team metrics.

### 7.5 Scale & ops (Q57–Q68)

57. Shard key for match index.  
58. Multi-region residency.  
59. Sync token design.  
60. Erasure SLO monitoring.  
61. Canonicalizer dual-write migration.  
62. Hot hmac (TV show SMS)?  
63. Capacity worksheet.  
64. Cell strategy.  
65. Failure injection tests.  
66. Suggestion cache TTL.  
67. Graph schema migrations.  
68. Cost narrative to VP.

### 7.6 Behavioral / Amazon (Q69–Q74)

69. Privacy SEV: discoverability bug — actions.  
70. Disagree: PM wants plaintext contact upload “for better match”.  
71. Frugality: cut FoF degree.  
72. Dive deep: whiteboard enumeration attack.  
73. Ownership across Graph vs Growth.  
74. Customer obsession: missed matches due to normalize bugs.

---

## 8. Appendices

### Appendix A — Data minimization matrix

| Data | Store? | Notes |
|------|--------|-------|
| Raw phone | No (prefer) | HMAC only |
| E.164 transient | Memory during HMAC | |
| Display name | Optional encrypted | UX |
| OS contact id | Optional | Delta sync |
| Call history | No | Out of scope |

### Appendix B — Example match index record

```json
{
  "hmac": "hmac_sha256:…",
  "kind": "phone",
  "user_ids": ["U_42"],
  "updated_at": 1754470000
}
```

### Appendix C — Sync request sketch

```json
{
  "sync_token": "t0",
  "contacts": [
    {"client_ref": "c1", "kind": "phone", "value": "+15551234567"}
  ]
}
```

### Appendix D — Rate limit table

| Subject | Hash lookups/day | Sync/hour | Friend req/day | Invites/day |
|---------|------------------|-----------|----------------|-------------|
| New | 1K | 10 | 20 | 3 |
| Normal | 10K | 60 | 100 | 10 |
| Trusted | 20K | 120 | 200 | 20 |

### Appendix E — PYMK score sketch

```text
score = 3.0 * log(1+mutuals) + 2.0 * co_contact + 0.5 * interaction - 5*ignored_recently
```

### Appendix F — Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| Store plaintext address books | Breach catastrophe |
| Public isRegistered API | Enumeration |
| Unbounded FoF nightly | Melts cluster |
| Ignore privacy settings in index | SEV |
| Infinite invites | SMS spam weapon |
| Log phones in clear | Compliance fail |

### Appendix G — Capacity worksheet

```text
Syncs/day _____ × contacts _____ × delta% _____ = upserts _____
Match lookups/s peak _____
Edges _____ ; avg degree _____ ; FoF cap _____ → candidates/user _____
Suggestions stored/user _____ × MAU _____ = KV size _____
```

### Appendix H — 45-minute timebox

| Min | Focus |
|-----|-------|
| 0–5 | Scope: sync, match, PYMK, privacy, RL |
| 5–12 | Estimates: upserts, FoF math, RL |
| 12–25 | HLD: HMAC index, graph, PYMK |
| 25–35 | Deep: enumeration OR erasure OR FoF caps |
| 35–42 | Scale 10×/100×/1,000× |
| 42–45 | Wrap-up trust |

### Appendix I — Glossary

| Term | Meaning |
|------|---------|
| PYMK | People You May Know |
| FoF | Friends of friends |
| HMAC | Hash-based message authentication code |
| E.164 | International phone format |
| Discoverability | Whether others can match you via contact |
| Delta sync | Upload only changes |
| Crypto-shred | Delete encryption key to erase data |

### Appendix J — Sample suggestions response

```json
{
  "items": [
    {
      "user_id": "U_99",
      "mutual_count": 3,
      "reasons": ["mutual_friends", "in_contacts"],
      "score": 0.82
    }
  ],
  "next_cursor": "…"
}
```

### Appendix K — Ownership RACI

| Activity | Contacts | Graph | PYMK | Privacy | T&S |
|----------|----------|-------|------|---------|-----|
| HMAC rotation | A | I | I | A | C |
| Discoverability default | C | I | C | A | C |
| FoF cap change | I | C | A | C | I |
| RL tiers | C | C | I | C | A |
| Erasure SLO | A | C | C | A | I |

### Appendix L — Progressive scale one-pager

| Scale | Bottleneck | Investment |
|-------|------------|------------|
| 10× | Match QPS + scrape risk | HMAC index, RL, batch PYMK |
| 100× | FoF compute + shards | Incremental, graph shard |
| 1,000× | Cells + residency + ML | Cells, approx, ANN, abuse ML |

### Appendix M — Comparison

| Topic | Answer |
|-------|--------|
| vs full social network | No feed/media focus |
| vs Twitter follow suggest | Contacts central; stronger privacy |
| vs CRM upload | Consumer consent + anti-scrape |
| vs password breach finders | Opposite ethics; minimize |

### Appendix N — Threat model

| Asset | Threat | Control |
|-------|--------|---------|
| Address book | Breach / insider | HMAC, minimize, access control |
| Registration oracle | Scraping | RL, no public API, anomaly |
| Users | Stalking via suggest | Blocks, ignores, mutual privacy |
| Platform | Invite spam | Quotas |
| Growth integrity | Fake match farms | Device reputation |

### Appendix O — Match pseudocode

```text
function match_chunk(user, contacts):
  assert settings.contact_sync_enabled
  rate_limit_check(user, len(contacts))
  out = []
  for c in contacts:
    h = hmac(normalize(c))
    upsert_user_contact(user, h, c.kind)
    for uid in index.get(h):
      if uid == user: continue
      if not discoverable(uid, c.kind): continue
      if blocked(user, uid): continue
      out.append(uid)
  return unique(out)
```

### Appendix P — Settings change

```text
on find_me_by_phone=false:
  for h in user.phone_hmacs:
    index.remove(h, user)
```

### Appendix Q — FoF expansion pseudocode

```text
function candidates(u):
  C = map()
  for f in top_interactive_friends(u, limit=100):
    if is_celeb(f): continue
    for fof in friends(f, limit=200):
      if fof in friends(u) or fof==u: continue
      C[fof].mutuals += 1
  return top_k(C, 500)
```

---

*End of Amazon SDE III prep doc — Find-Friends Service System Design.*
