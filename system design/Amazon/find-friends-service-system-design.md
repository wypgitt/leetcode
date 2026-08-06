# System Design: Find Friends Service (PYMK / People You May Know)

> **Focus areas:** Contact import · Graph embeddings/features · Candidate generation · Ranking · Privacy · Abuse · Opt-out · Serving latency · Batch vs nearline · Cells
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Privacy of address books; no creepy over-sharing; online serving ≠ heavy offline join; abuse/spam invites controlled
> **Interview theme:** Amazon SDE III / L6 — **Find Friends / PYMK** service with Amazon trust & frugality bar

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

Goal: design a **Find Friends / People You May Know (PYMK)** service that suggests users to connect with (friend/follow), using signals like mutual friends, contact sync, workplace/school, interactions, and optional ML rankers—with strict privacy and abuse controls.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Candidate generation + rank + serve suggestions | Full social network / feed |
| Graph | Reads social graph + contact graph | Owns all of Messenger |
| Output | Ranked list of user cards + reasons (careful) | Ads targeting platform |
| Amazon lens | Privacy, consent, abuse, cost, ownership | Creepy maximal data joins |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Surfaces? | PYMK widget, invite friends, search people | Multiple clients; one service |
| F2 | Contact sync? | Optional upload hashed contacts | Consent + retention policy |
| F3 | Mutual friends? | Primary signal | Graph features |
| F4 | Other signals? | Work/edu, co-interactions, follows | Feature store |
| F5 | Actions? | Add friend / follow / dismiss / snooze | Feedback loop |
| F6 | Reasons UI? | "N mutual friends" careful copy | Explainability constraints |
| F7 | Blocks? | Never suggest blocked; honor ignore | Authz filters |
| F8 | Invites? | Email/SMS invite non-users | Rate limits + spam law |
| F9 | Opt-out? | Don't suggest me / don't use my contacts | Mandatory |
| F10 | Freshness? | Nearline ok; not every click recompute all | Batch + nearline |
| F11 | Search people? | Typeahead separate or light overlap | Don't merge blindly |
| F12 | Abuse? | Invite spam, scraping suggestions | Limits + detection |

**MVP scope:**

1. Consent-gated contact import (hashed).  
2. Candidate generators: mutual friends, contact match, simple affinity.  
3. Ranker (heuristic MVP; ML Phase 1.5).  
4. Serve top-K with caching.  
5. Dismiss/snooze feedback.  
6. Block/opt-out filters.  
7. Invite non-users with strict rate limits.  
8. Metrics + abuse dashboards.

**Out of MVP:** full GNN training platform thesis; shadow profiles without consent; infinite contact retention; cross-product ads join.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Serve p99 | < 100–200ms cached; < 300–500ms recompute path |
| N2 | Privacy | Consent, minimization, deletion SLO |
| N3 | Accuracy freshness | Batch hours; nearline minutes for edges |
| N4 | Availability | Widget degrade to empty/cached > hard fail page |
| N5 | Invite compliance | Regional SMS/email laws; opt-out |
| N6 | Abuse | Invite/day caps; scrape resistance |
| N7 | Cost | Feature compute bounded per user/day |
| N8 | Explainability | Safe reasons only |

### 1.3 Cases

**Happy:** sync contacts → match users → PYMK shows mutuals → add friend.

**Edges:** celebrity match via contact; stalker patterns; dismiss ignored; remarried name collisions; work email shared; EU deletion; bot invites; graph party (dense); empty graph new user; false contact match; "why am I suggested" support.

| Case | Behavior |
|------|----------|
| User deletes contacts | Drop derived edges within deletion SLO; stop using |
| Block | Bidirectional exclusion from candidates |
| Dismiss | Negative signal; suppress period |
| Dense mutual graph | Cap candidates; diversity |
| New user cold start | Contacts + import prompts; popular/local weak fallback carefully |
| Invite spam | Hard caps; device reputation; templates |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| MAU | 10M | 100M | 1B | — |
| PYMK requests/day | 50M | 500M | 5B | — |
| Peak serve QPS | 2K | 20K | 200K | — |
| Contact uploads/day | 1M | 10M | 100M | — |
| Graph edges | 1B | 10B | 100B | — |
| Candidates scored/user | 500 | 500 | 1K | — |
| Invites/day | 2M | 20M | 200M | — |

**Jumps:** 10× feature store + cache; 100× sharded graph features + nearline; 1,000× cellized privacy compute, advanced retrieval, stricter minimization.

### 1.5 Scope repeat-back

> Find-friends/PYMK: consentful contact match + graph candidate generation + ranking + serve top-K with dismiss feedback, blocks/opt-outs, invite abuse controls—batch/nearline compute with online cheap serve—Amazon privacy bar.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Serve vs compute

```text
If every PYMK request does 2-hop graph walk online:
200K QPS × expensive walks = death

Therefore: precompute candidate sets per user (batch/nearline);
online: fetch cached list + light re-rank + filters
```

### 2.2 Mutual friends cost

```text
2-hop expansion naive is huge on dense graphs
Use: precomputed friend-of-friend counts / inverted indexes / sketches
Cap expansion; prioritize high-affinity nodes
```

### 2.3 Contact match

```text
Hash (HMAC salted) phone/email → lookup user index
1M uploads/day × 500 contacts = 500M lookups → batch/stream workers not inline
```

### 2.4 Storage

```text
Per user top-K list (~100 IDs + scores + reason codes) ≈ 2–5 KB
100M users × 3 KB ≈ 300 GB suggestions store (plus versions)
Contact hashes retention minimized
```

### 2.5 Latency budget (serve)

```text
Edge auth → cache get → filter block/dismiss → light rerank → hydrate profiles
Budget ~20+30+20+50+50 ms
```

### 2.6 Bottlenecks

(1) 2-hop explosion (2) contact upload storms (3) profile hydration (4) privacy deletions (5) invite provider limits (6) feature staleness bugs.

### 2.7 Cost / frugality

Graph compute and SMS invites dominate. Cap daily recompute; aggressive dismiss suppression; SMS last resort.

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Consent/Privacy | Permissions, retention, deletion | Strong policy |
| Contact Match | Hashed contact index | Eventual match edges |
| Graph Features | Mutuals, embeddings | Batch/nearline |
| Candidate Sets | Per-user pools | Eventual |
| Rank/Serve | Online top-K | Read optimized |
| Feedback | Dismiss/accept | Durable events |
| Invite | Non-user invites | Rate-limited |
| Abuse | Spam/scrape | Realtime limits |

**Deal-breaker:** uploading raw address books to long-lived plaintext logs.

### 3.2 Components

1. **PYMK API** — serve suggestions, dismiss, settings  
2. **Consent Service** — contact sync permissions  
3. **Contact Ingest** — hash, normalize, match workers  
4. **Graph Feature Jobs** — mutuals, interactions  
5. **Candidate Builder** — merge generators, score  
6. **Suggestions Store** — per-user lists (Dynamo/Cassandra/Redis)  
7. **Online Filter/Rerank** — blocks, opt-outs, freshness  
8. **Profile Hydration** — cards  
9. **Feedback Stream** — accepts/dismisses → training/rules  
10. **Invite Service** — email/SMS with compliance  
11. **Abuse/Rate Limit**  
12. **Deletion/GC Worker**  

### 3.3 APIs (sketch)

```text
POST /v1/contacts/sync  {hmac_contacts[], consent_token}
GET  /v1/pymk?limit=20&cursor=
POST /v1/pymk/dismiss {user_id, reason?}
POST /v1/pymk/snooze  {user_id, days}
POST /v1/invites      {channel, target_hash_or_addr}
GET  /v1/settings/privacy
```

### 3.4 Candidate generators

```text
G1 Mutual friends (capped)
G2 Contact match
G3 Co-interaction (likes/comments/reshares) weak
G4 Work/edu metadata match (opt-in fields)
G5 Follow-of-follow (IG-like)
Merge → score → top pool → store
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Online 2-hop | Avoid heavy | Latency/cost |
| Contact hashing | HMAC server salt + normalize | Privacy |
| Reasons | Coarse safe reasons | Anti-creepy |
| Recompute | Daily + nearline edge triggers | Fresh enough |
| Invites | Strict caps | Spam law / trust |
| ML | After heuristics | Bias/privacy review |

---

## 4. Architecture Diagram

```text
Client → PYMK API → Suggestions Cache/Store → Online Filters → Profile Service
              ^                ^
              |                |
         Feedback Events   Candidate Builder <── Graph Features
                                   ^
                                   |
              Contact Ingest → Match Index
                                   |
                              Consent/Privacy DB

Invite API → Compliance checks → Email/SMS providers
Abuse limits on API + Invite
```

### 4.1 Contact sync sequence

```text
1. Client obtains consent
2. Normalize contacts client-side; send HMAC with server pepper rotation policy
3. Ingest durable encrypted-at-rest minimal fields
4. Match to users; emit match edges
5. Trigger candidate rebuild nearline for uploader (+ carefully for matched users per policy)
```

### 4.2 Serve sequence

```text
1. Auth
2. Load precomputed list
3. Filter: block, opt-out, dismiss, already friends, deactivated
4. Optional light rerank with online features
5. Hydrate; return with safe reason codes
```

### 4.3 Deletion sequence

```text
User revokes contact consent → delete contact rows → remove match edges →
rebuild suggestions → audit log of deletion completion
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. No suggestions violating block/opt-out.  
2. Contact data used only with consent; deletable.  
3. Serve path does not require full graph walk.  
4. Idempotent dismiss.  
5. Invite sends respect caps and suppression lists.  
6. Reasons never reveal sensitive inferred data ("synced from your ex's phone" forbidden).  
7. Degrade to empty list > wrong privacy.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Nightly batch mutuals; Redis lists; PG contacts |
| 10× | Stream contact match; feature store; sharded suggestions |
| 100× | Nearline graph; cell privacy; approx mutual sketches |
| 1000× | Advanced retrieval (ANN embeddings) with policy gates; regional isolation |

### 5.3 Maintainability

- Generator plugins with kill switches  
- Shadow ranking for ML  
- Privacy unit tests + red-team  
- Data retention configs as code  
- Replay candidate builds for a user (debug tool with audit)  

### 5.4 Progressive scale

**1×:** heuristics; nightly.  
**10×:** streaming ingest; cached serve.  
**100×:** nearline; cells; invite platform mature.  
**1000×:** embedding retrieval + strict policy; multi-region deletion SLOs.

### 5.5 Mutual-friends algorithms (interview level)

- Inverted index: for each user, friends list compressed  
- Estimate |F(a) ∩ F(b)| via intersection on smaller list  
- Precompute top FoF candidates offline with priority queue  
- Cap degree: skip expanding mega-nodes or treat specially  

### 5.6 Creepy suggestion problem

- Limit reason taxonomy  
- Don't use sensitive inferred edges in UI  
- Avoid suggesting based solely on ephemeral location without clear UX  
- Support "Why am I seeing this?" with audited safe explanation  

### 5.7 Abuse

- Per-account invite daily caps; velocity on new accounts  
- Suggestion scraping: pagination tokens, rate limits, anomaly  
- Fake mutuals via bot rings: graph integrity scores  

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Raw contacts in logs | Privacy catastrophe |
| Online unbounded 2-hop | Latency melt |
| Suggest blocked users | Trust SEV |
| SMS invite loops | Carrier ban + legal |
| Shadow profiles without consent | Regulatory SEV |
| Ads join on critical PYMK path | Scope creep / privacy |

---

## 6. Wrap-Up

### 6.1 Designed

Consentful contact match + graph candidate builders + ranked suggestions store + online filters + feedback + invite compliance + abuse—cheap online serve.

### 6.2 Decisions to defend

1. Precompute candidates; cheap serve  
2. HMAC/minimized contacts + deletion SLO  
3. Safe reason codes  
4. Block/opt-out hard filters online  
5. Nearline + batch hybrid compute  
6. Invite caps  
7. Kill switches per generator  
8. Empty degrade > wrong  

### 6.3 Risks

Privacy incidents; creepy UX; graph compute cost; invite spam; ML bias.

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope PYMK not full FB |
| 5–15 | Privacy/consent/contacts |
| 15–28 | Generators + precompute |
| 28–38 | Serve path + filters + invites |
| 38–45 | Scale, abuse, ownership |

### 6.5 Closer

> **Find Friends/PYMK**: privacy-minimized signals, precomputed candidates, online hard filters, safe explanations, invite compliance, progressive scale—trust over maximal recall.

---

## 7. Deeper / Related Interview Questions

### 7.1 Privacy

**Q: Salt/pepper strategy?**  
A: Server-side pepper; rotation with rehash jobs; never store reversible phone if policy forbids.

**Q: Matched user notification "someone has your number"?**  
A: Usually **no**—creepy and unsafe. Product policy.

### 7.2 Graph

**Q: Celebrity in FoF?**  
A: Degree caps; don't explode through celebs.

**Q: Directed follow PYMK?**  
A: Different generators (FoF, engagement); still filters.

### 7.3 Ranking

**Q: Features?**  
A: mutual count, contact match strength, interaction score, recency, penalties (dismiss).

**Q: Offline eval?**  
A: accept rate, downstream session quality, complaint rate, block rate after suggest.

### 7.4 Invites

**Q: Email vs SMS?**  
A: Email cheaper; SMS higher friction/compliance; double opt-in regional rules.

### 7.5 Interview traps

**Q: Neo4j online for every request at 1B?**  
A: Unlikely as sole serve path.  
**Q: Keep contacts forever for better match?**  
A: Violates minimization.  
**Q: Show exact contact contributor?**  
A: Often unsafe.

### 7.6 Metrics

| Metric | Why |
|--------|-----|
| serve_p99 | UX |
| accept_rate | Quality |
| dismiss_rate | Irrelevance/creepy |
| complaint_rate | Trust |
| deletion_slo_miss | Privacy |
| invite_block_rate | Abuse |
| compute_$ / MAU | Frugality |
| filter_drop_rate | Authz health |

### 7.7 Ownership

Privacy deletion miss → Privacy Eng + PYMK. Bad creepy spike → PYMK Science+Product+Trust. Invite carrier ban → Invite platform.

### 7.8 Progressive drill

10× cache+stream; 100× nearline+cells; 1000× embedding retrieval with policy.

### 7.9 Cold start

Prompt contact sync; import FB/Google carefully with consent; weak geo/popular only if product allows (often skip).

### 7.10 Relation to social network doc

PYMK is a satellite; must not block feed path; consumes graph snapshots/events.

---

## 8. Appendices

### 8.1 Schema sketches

```text
consent(user_id, contact_sync, updated_at)
contact_hashes(user_id, hash, type, last_seen)
match_edges(user_id, matched_user_id, strength, sources[])
suggestions(user_id, cand_user_id, score, reason_code, computed_at)
dismissals(user_id, cand_user_id, until_ts)
opt_outs(user_id, do_not_suggest, do_not_use_contacts)
invites(invite_id, sender_id, channel, target_fingerprint, state, ts)
```

### 8.2 API checklist

- [ ] Consent + sync  
- [ ] PYMK get  
- [ ] Dismiss/snooze  
- [ ] Privacy settings  
- [ ] Invites  
- [ ] Deletion  
- [ ] Admin debug (audited)  

### 8.3 Oncall checklist

- [ ] Serve p99  
- [ ] Empty-rate spike  
- [ ] Complaint spike  
- [ ] Deletion backlog  
- [ ] Invite provider errors  
- [ ] Generator job lag  
- [ ] Cache stampede  
- [ ] Scrape detection  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| PYMK | People You May Know |
| FoF | Friend of friend |
| HMAC contact | One-way contact token |
| Reason code | Safe explanation enum |
| Nearline | Minutes-latency stream compute |
| Suppression | Dismiss/opt-out/block lists |

### 8.5 Deal-breaker one-liners

- Plaintext address books in warehouse without control  
- Online mega 2-hop  
- Suggesting blocked users  
- Uncapped SMS blasts  

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Serve API | PYMK Serving |
| Generators | PYMK Science/Eng |
| Contacts | Identity/Privacy |
| Invites | Growth + Compliance |
| Abuse | Trust |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | Nightly Spark/SQL + Redis |
| 10× | Kafka match + sharded suggestions |
| 100× | Nearline FoF; cells |
| 1000× | ANN retrieval + regional privacy |

### 8.8 Failure injection

1. Feature job fail → serve stale cache with TTL cap; then empty.  
2. Contact DB delete lag → privacy SEV page.  
3. Ranker bad → heuristic fallback.  
4. Invite provider down → queue with cap; don't retry storm.  
5. Celebrity expansion bug → CPU melt; kill generator.

### 8.9 Reason code catalog (safe)

`MUTUAL_FRIENDS`, `IN_CONTACTS`, `SHARED_NETWORK`, `POPULAR_IN_AREA` (if allowed)—never `VIEWED_YOUR_PROFILE` unless product explicitly and safely supports.

### 8.10 Feedback learning

Accept/dismiss events → daily retrain / rule tune; explore/exploit careful; complaint hard negative.

### 8.11 Interview closer checklist

- [ ] Precompute vs online walk  
- [ ] Contact privacy  
- [ ] Filters  
- [ ] Invites  
- [ ] Kill switches  
- [ ] Metrics  
- [ ] Scale jumps  

### 8.12 Related

Social graph service, people search autocomplete, growth invites, trust & safety, notifications ("friend joined").

### 8.13 Sample events

```text
CONSENT_GRANTED, CONTACTS_SYNCED, MATCH_FOUND, CANDIDATES_BUILT,
SUGGESTION_SHOWN, SUGGESTION_ACCEPTED, SUGGESTION_DISMISSED,
INVITE_SENT, CONSENT_REVOKED, DATA_DELETED
```

### 8.14 Regionalization

EU deletion SLOs tighter; SMS rules vary; keep compute cells regional when required.

### 8.15 Security

Authz on serve; prevent ID enumeration via suggestion API; pad times; audit debug tools.

### 8.16 Cost narrative

Graph jobs + SMS. Frugality: recompute active users more often than dormant; email > SMS.

### 8.17 LP hooks

Customer Obsession = creepy/complaints; Frugality = compute caps; Earn Trust = consent/deletion; Dive Deep = false match incidents; Ownership = privacy miss pages.

### 8.18 QoS degrade order

1. Turn off experimental generators  
2. Skip light rerank  
3. Serve last-known list  
4. Empty widget  
5. Never serve unfiltered graph walk results  

### 8.19 Hash collision handling

Use 128-bit+ hashes; include type; rare collisions → secondary confirmation signals before high-confidence match.

### 8.20 Relationship to Amazon

Internal tools may "find colleagues"; still apply minimization and abuse—don't assume corporate directory replaces consent for personal contacts.

---

## Deep Technical Notes — Find Friends

### Normalization

E.164 phones; email lowercase + Gmail dot handling policy; conflict rules documented.

### Sketch mutual counts

MinHash/bottom-k for rough FoF; exact re-rank top candidates.

### Triggered rebuild

On friend accept / contact sync / dismiss threshold—debounce per user.

### Embedding ANN (1000×)

Two-tower user embeddings; ANN retrieve → policy filter → rank; watch feedback loops.

### Debug tooling

"Compute explanation for user A→B" restricted, audited, rate-limited, no raw contacts shown.

---

## Worked Capacity Narrative — Find Friends

Online QPS is easy if lists are precomputed; graph science is the iceberg. Interviewers listen for whether you accidentally put Spark behind a user click.

## Customer-Trust Paragraph — Find Friends

Address books are intimate. Leaks, creepy reasons, and un-deletable syncs destroy trust faster than low accept rate. Empty PYMK is better than a privacy incident.

## Progressive Scale Recap — Find Friends

- **10×:** stream match + cached serve  
- **100×:** nearline graph + cells  
- **1,000×:** ANN retrieval + regional privacy compute  

## Supplemental Depth Pack — Find Friends

### S1. Precomputed suggestions

Batch/nearline candidate pools; online fetch+filter.
**Invariant:** No unbounded online 2-hop at serve QPS.
**Metric:** serve_p99, recompute_lag.
**Ownership:** PYMK Serving.

### S2. Contact privacy

Consent, HMAC, minimization, deletion SLO.
**Invariant:** Revocation removes use within SLO.
**Metric:** deletion_slo_miss.
**Ownership:** Privacy + Contacts.

### S3. Hard online filters

Block, opt-out, dismiss, existing edge, deactivated.
**Invariant:** Filtered users never returned.
**Metric:** filter_probe_fail=0.
**Ownership:** PYMK Serving.

### S4. Safe reasons

Enum-only explanations; no sensitive inference leakage.
**Invariant:** Reason taxonomy reviewed.
**Metric:** complaint_rate.
**Ownership:** Product + PYMK.

### S5. Invite compliance

Caps, suppression, regional rules, templates.
**Invariant:** No invite storms.
**Metric:** invites_blocked, provider_error.
**Ownership:** Growth/Compliance.

### S6. Generator kill switches

Disable FoF/contact/embedding independently.
**Invariant:** Bad generator can be shed.
**Metric:** generator_error_rate.
**Ownership:** PYMK Eng.

### S7. Feedback loop

Accept/dismiss → retrain/rules; hard negatives on reports.
**Invariant:** Dismiss suppresses for period.
**Metric:** re-show_after_dismiss_rate.
**Ownership:** Science + Serving.

### S8. Cells / regionalization

Privacy and compute isolation; directory of home cell.
**Invariant:** Cross-region raw contact movement minimized.
**Metric:** cross_region_contact_bytes≈policy.
**Ownership:** Platform + Privacy.

## Scenario Runbooks — Find Friends

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|-----------|
| Creepy complaint spike | Disable risky generator/reasons | Fewer suggestions | Audit features |
| Deletion SLO miss | Page; halt secondary use; accelerate GC | Privacy | Capacity/process |
| Serve p99 fire | Serve stale/empty; scale cache | Widget degrade | Hot key |
| Invite spam wave | Tighten caps; freeze new accounts | Growth ↓ | Abuse model |
| False contact matches | Raise match threshold | Recall ↓ | Normalization fix |
| FoF job explosion | Kill mega-node expansion | Stale mutuals | Degree caps |
| Scrape detected | Rate limit tokens | API stricter | WAF rules |
| Empty-rate spike | Check job lag/filters bug | UX | Pipeline |

## Rapid-Fire Q&A — Find Friends

**RQ1. Why precompute?**  
**A:** Serve QPS cannot afford heavy graph walks.

**RQ2. Test precompute?**  
**A:** Rebuild fixtures; lag SLOs; canary users.

**RQ3. 100× without precompute?**  
**A:** Latency/cost melt.

**RQ4. Why HMAC contacts?**  
**A:** Minimization; reduce plaintext exposure.

**RQ5. Test deletion?**  
**A:** Consent revoke drills; warehouse lineage checks.

**RQ6. Regression?**  
**A:** Regulatory/trust SEV.

**RQ7. Why online filters?**  
**A:** Edges change faster than batch.

**RQ8. Test filters?**  
**A:** Block probes continuous.

**RQ9. Regression?**  
**A:** Trust SEV.

**RQ10. Why safe reasons?**  
**A:** Prevent creepy/harmful explanations.

**RQ11. Test reasons?**  
**A:** Policy review + complaint taxonomy.

**RQ12. Regression?**  
**A:** Brand/trust damage.

**RQ13. Why invite caps?**  
**A:** Spam/legal/carrier risk.

**RQ14. Test invites?**  
**A:** Abuse simulations; provider sandboxes.

**RQ15. Regression?**  
**A:** Bans + user harm.

**RQ16. Why kill switches?**  
**A:** Generators misfire in production.

**RQ17. Test kill switches?**  
**A:** Game day disable; measure empty/accept.

**RQ18. Regression?**  
**A:** Stuck shipping bad suggestions.

**RQ19. Why dismiss durable?**  
**A:** Re-showing angers users.

**RQ20. Test dismiss?**  
**A:** Idempotency + suppression windows.

**RQ21. Regression?**  
**A:** Dismiss_rate↑ complaints↑.

**RQ22. Why cells?**  
**A:** Privacy/residency + blast radius.

**RQ23. Test cells?**  
**A:** Regional failover without contact exfil.

**RQ24. Regression?**  
**A:** Global privacy blast radius.

## Narrative Walkthrough — Find Friends

### Beat 1
Consent + contact sync hashed. Tradeoff: recall vs privacy minimization.

### Beat 2
Match workers create edges. Tradeoff: threshold vs false positives.

### Beat 3
Batch FoF candidates + merge generators. Tradeoff: coverage vs compute.

### Beat 4
Store top pool; serve with filters. Tradeoff: freshness vs cost.

### Beat 5
User dismisses; suppress; feedback event. Tradeoff: explore vs respect.

### Beat 6
Invite non-user with caps. Tradeoff: growth vs spam.

### Beat 7
10×/100×/1000× compute evolution. Tradeoff: ML lift vs policy risk.

### Beat 8
Deal-breakers: plaintext contacts; online 2-hop; ignore blocks. Economics: jobs + SMS.

## Pre-Onsite Checklist — Find Friends

- [ ] Precompute narrative
- [ ] Contact consent/deletion
- [ ] Online filters
- [ ] Safe reasons
- [ ] Invite compliance
- [ ] Generator kill switches
- [ ] Metrics + owners
- [ ] Progressive scale
- [ ] Creepy SEV story
- [ ] Relation to social graph/feed
- [ ] Cold start
- [ ] Scrape resistance
- [ ] Empty degrade policy
- [ ] SDM trust-first pitch
- [ ] Runbooks

### Extra drill

In 90 seconds: explain why "just query Neo4j for FoF on each page view" fails at 100×, and what you do instead.

### Extra drill

Write the privacy deletion sequence on a whiteboard with SLOs and owners.

---

*End of document — Find Friends Service (Amazon Interview Style) (SDE III)*

## Extra Interview Drills — Find Friends

### Extra Interview Drills — Find Friends — item 1

**Prompt:** 60s drill on theme 1: bottleneck, invariant, metric, kill switch, owner.

**Strong answer shape:**
- Plane + progressive scale jump
- What you shed first vs what stays correct
- One deal-breaker alternative

**Trap:** Treating theme 1 as a pure offline batch problem with no online abuse/privacy controls.


### Extra Interview Drills — Find Friends — item 2

**Prompt:** 60s drill on theme 2: bottleneck, invariant, metric, kill switch, owner.

**Strong answer shape:**
- Plane + progressive scale jump
- What you shed first vs what stays correct
- One deal-breaker alternative

**Trap:** Treating theme 2 as a pure offline batch problem with no online abuse/privacy controls.


### Extra Interview Drills — Find Friends — item 3

**Prompt:** 60s drill on theme 3: bottleneck, invariant, metric, kill switch, owner.

**Strong answer shape:**
- Plane + progressive scale jump
- What you shed first vs what stays correct
- One deal-breaker alternative

**Trap:** Treating theme 3 as a pure offline batch problem with no online abuse/privacy controls.


### Extra Interview Drills — Find Friends — item 4

**Prompt:** 60s drill on theme 4: bottleneck, invariant, metric, kill switch, owner.

**Strong answer shape:**
- Plane + progressive scale jump
- What you shed first vs what stays correct
- One deal-breaker alternative

**Trap:** Treating theme 4 as a pure offline batch problem with no online abuse/privacy controls.


### Extra Interview Drills — Find Friends — item 5

**Prompt:** 60s drill on theme 5: bottleneck, invariant, metric, kill switch, owner.

**Strong answer shape:**
- Plane + progressive scale jump
- What you shed first vs what stays correct
- One deal-breaker alternative

**Trap:** Treating theme 5 as a pure offline batch problem with no online abuse/privacy controls.


### Extra Interview Drills — Find Friends — item 6

**Prompt:** 60s drill on theme 6: bottleneck, invariant, metric, kill switch, owner.

**Strong answer shape:**
- Plane + progressive scale jump
- What you shed first vs what stays correct
- One deal-breaker alternative

**Trap:** Treating theme 6 as a pure offline batch problem with no online abuse/privacy controls.

