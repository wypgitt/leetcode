# System Design: Instagram Auction Feature (Meta)

> **Focus areas:** Bidding · Atomic ledger · Fairness · Realtime updates · Fraud · Scale isolation from core IG  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split bid-write vs feed-browse vs settlement planes, explicit money/ledger deal-breakers  
> **Interview theme:** Meta product L5+ — add **auctions** inside Instagram (creator/brand drops, charity, limited merch) without breaking IG’s read-heavy social core

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

Goal: **bound the product**—an **auction feature inside Instagram**: creators/brands list items, users bid in realtime, auction ends with a winner, payment/settlement hooks, anti-sniping/fraud controls, and isolation from core feed infra.

### 1.0 What this is / is not

| Dimension | **IG Auction (this doc)** | Not this |
|-----------|---------------------------|----------|
| Primary job | Run timed auctions with correct winner & bids | Full Shopify/marketplace ERP |
| Success | Fair bidding, correct settlement, trust | Perfect global inventory for all commerce |
| Data plane | Auction state + bid ledger + realtime | IG feed ranking ML |
| Query | Auction page, bid history, watch list | Ad auction (ads ranking is different!) |
| Correctness | Strong for bid accept / winner | Eventual OK for view counts |

**Scope statement:** Design Instagram-native auctions (listing → bid → end → pay → fulfill hooks), not the ads auction exchange.

**Say early:** This is **product commerce auction**, not **ads auction**. Confusing them is an interview fail.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Auction type? | English ascending timed; optionally reserve/buy-now | State machine per auction |
| F2 | Who sells? | Verified creators/brands MVP | Seller onboarding + KYC hooks |
| F3 | Bid currency? | Real money via Payments; or in-app credits Phase | Ledger + payment intents |
| F4 | Soft close / anti-snipe? | Extend end if bid near deadline | End-time mutation rules |
| F5 | Proxy / max bid? | Optional automatic up-to-max | Proxy bid engine |
| F6 | Realtime UI? | Current price, bid count, countdown | Pub/sub per auction |
| F7 | Visibility? | Public IG post/story entry points | Link auction_id to media |
| F8 | Winner flow? | Pay within T; else offer next | Settlement state machine |
| F9 | Shipping/fulfill? | Hooks to existing commerce; MVP mark paid | Outbox to fulfillment |
| F10 | Moderation? | Banned items; fraud bids | Policy + risk scores |
| F11 | Notifications? | Outbid, winning, ending soon | Notif bus |
| F12 | International? | Multi-currency Phase 1.5 | Money with currency codes |

**MVP functional scope:**

1. Seller creates auction: item, start price, reserve optional, start/end time, media.  
2. Users place bids ≥ min increment above current.  
3. Realtime updates of price/leader on auction page.  
4. Anti-snipe soft-close extension (e.g. +2 min if bid in last 2 min), capped.  
5. On end: determine winner; create payment intent; handle pay failure → next eligible.  
6. Bid ledger immutable; audit trail.  
7. Selller/buyer notifications; basic fraud checks.  
8. Watch / remind.

**Out of MVP:**

- Full multi-lot complex auction houses  
- Dutch/Vickrey as primary (mention only)  
- Cross-border tax engine deep dive  
- Ads auction / IRIS ranking  
- Guaranteed sub-ms global bid lock without region home

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Bid accept latency | Feels instant | p99 < 200–400ms regional |
| N2 | Bid correctness | No lost accepted bids; correct winner | Strong serializability per auction |
| N3 | End-time fairness | Clear rules | Deterministic end + extensions |
| N4 | Availability | Auction page critical near end | 99.9%+; degrade browse not bidding |
| N5 | Realtime lag | Countdown & price | p99 < 1–2s fanout |
| N6 | Auditability | Disputes | Immutable bid log |
| N7 | Isolation | Don’t melt IG feed | Separate auction cell |
| N8 | Fraud | Payment/risk | Risk scoring before accept/settle |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Creator publishes auction post → users open → place bid → see price update live.  
2. User sets max proxy bid → system auto-bids min increment until max.  
3. Bid in last seconds → soft-close extends end → more bids → ends → winner pays.  
4. Winner payment fails → second-highest gets offer window.  
5. User outbid → push notification → returns to bid again.  
6. Auction with reserve not met → no winner / seller options.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click bid | Idempotency-Key; one bid |
| Concurrent bids | Serialize per auction; one winner ordering |
| Bid after end | Reject with terminal state |
| Payment timeout | Relist offer to next; state transitions logged |
| Seller cancels mid | Policy: only before first bid or with penalties |
| Fraud stolen card | Risk hold; freeze settlement |
| Clock skew clients | Server authoritative end_ts |
| Hot auction 100K watchers | Coalesced fanout; bid path isolated |
| Currency mismatch | Reject; single currency per auction MVP |
| Shill bidding | Velocity/graph signals; investigate |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active auctions | 10K | 100K | 1M | 10M |
| Bids/day | 5M | 50M | 500M | 5B |
| Peak bids/s global | 2K | 20K | 200K | 2M |
| Peak bids/s one auction | 200 | 2K | 10K | specialized |
| Concurrent watchers / auction | 50K | 500K | 5M | edge tree |
| Auction page QPS | 50K | 500K | 5M | cache |
| Settlements/day | 50K | 500K | 5M | payments scale |
| Avg bid payload | ~200 B | 200 B | 200 B | 200 B |

**What each jump forces:**

- **10×:** Per-auction single-writer; Redis/realtime; payments async.  
- **100×:** Auction cells; hierarchical live fanout; risk platform.  
- **1,000×:** Shard by auction_id heavily; proxy bidding workers; edge watches.

### 1.5 Etc. (Constraints & Assumptions)

- Instagram identity, feed, media already exist — auction **links** to media_id.  
- Payments via Meta commerce / Payments service — we orchestrate intents.  
- Legal/compliance: auctions may be geo-gated; mention hooks.  
- Server time is authoritative for start/end.

**Scope statement to repeat back:**

> Design an Instagram product auction system: listings, strongly consistent per-auction bidding with ledger, soft-close, realtime watchers, payment settlement state machine, fraud hooks—isolated from core IG feed—and scale through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Browse auction pages** | Read current state | 50K QPS | Cache |
| **Place bid** | Strong write | 2K/s | Auction engine |
| **Proxy auto-bids** | Derived writes | subset | Engine workers |
| **Live fanout** | Price updates | coalesced | Pub/sub |
| **Settlement** | Payments | lower QPS | Workflow |
| **Notifications** | Outbid etc. | async | Notif |
| **Risk** | Score bids | on write | Risk |

**Anti-pattern:** mixing ads bid requests (millions QPS) with product auction bids.

### 2.2 Hot auction math

```text
200 bids/s on one auction × serialize = needs single-threaded or ordered log ~OK
50K watchers × 200 events/s = 10M msgs/s naive → coalesce to 5–10 updates/s
```

### 2.3 Storage

```text
5M bids/day × 300 B ≈ 1.5 TB/day raw log (upper)
Active auction state tiny (10K × few KB)
Keep immutable bid log in append store; state in OLTP
```

### 2.4 Soft-close amplification

```text
Popular auction ends: last 2 minutes may produce huge bid spike
Engine must be pre-warmed; page cache short TTL; live coalesce
```

### 2.5 Money

```text
Never store “balance” only in cache
Ledger: append-only entries; settlement workflows idempotent
Payments service is source for capture/refund
```

### 2.6 Inventory hold arithmetic

```text
Listing creates inventory_hold on item (qty=1 unique) until ENDING/void
Concurrent auctions same item_id: reject or serialize via hold service
Hold TTL ≥ auction max duration + settlement grace
At 10K live auctions: 10K holds — trivial count; correctness > QPS
```

### 2.7 Bid path latency budget

```text
auth + risk soft checks     5–20ms
enqueue / lock auction      1–5ms
validate + apply            <1–3ms CPU
persist bid log + state     5–20ms
ACK                         total p99 < 100–200ms
live tick publish           async coalesce 100–200ms
```

### 2.8 Soft-close load spike

```text
Last 2 minutes: bid rate ×5–20 vs average
Proxy cascades: one max raise may generate few system bids — still serial
Watcher ticks: coalesce to ≤10/s even if bids 200/s
Closer job: wake at end_ts; must be HA (leader election)
```

### 2.9 Settlement throughput

```text
Ended auctions/day 100K; settlement workflows 100K starts
PSP capture p95 seconds–minutes — async OK
Idempotency keys: settlement_id = auction_id
Retry storms must not double-capture
```

### 2.10 Fraud scoring cost

```text
Sync risk budget ≤10–20ms features (account age, velocity, graph edges cached)
Heavy ML async: may freeze payout not block bid ACK (policy)
False positive: dispute tooling reconstructs from bid log
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/auctions` | Seller create |
| `GET /v1/auctions/{id}` | Public state (price, end, leader masked) |
| `POST /v1/auctions/{id}/bids` | Place bid / proxy max |
| `GET /v1/auctions/{id}/bids` | History paginated |
| `POST /v1/auctions/{id}/watch` | Watch |
| `WS /v1/auctions/{id}/live` | Realtime events |
| `POST /internal/auctions/{id}:close` | Closer worker |
| `POST /v1/auctions/{id}/settlement` | Payment orchestration callbacks |

**Bid request:**

```text
BidRequest {
  auction_id,
  bidder_id,
  amount,           // or max_amount for proxy
  currency,
  idempotency_key,
  client_ts
}
```

### 3.2 State machine (auction)

```text
DRAFT -> SCHEDULED -> LIVE -> ENDING -> ENDED
                              |
                              v
                         SETTLEMENT -> PAID -> FULFILLING -> COMPLETE
                                         |
                                         v
                                      DEFAULTED -> OFFER_NEXT -> ...
Reserve not met: ENDED_NO_WINNER
```

### 3.3 Data model

| Entity | Key | Notes |
|--------|-----|-------|
| Auction | `auction_id` | state, prices, times, seller, media_id |
| Bid log | `(auction_id, bid_id)` | immutable append |
| High bid state | `auction_id` | current_price, leader, version |
| Proxy | `(auction_id, user_id)` | max_amount |
| Settlement | `auction_id` | payment intents, attempts |
| Watch | `(auction_id, user_id)` | |

### 3.4 Bid engine — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Single-writer per auction** (actor / serial queue) | Correctness easy | Hot auction CPU bound | **MVP best** |
| DB row lock `SELECT FOR UPDATE` | Simple | Connection pileup | Low-medium |
| Optimistic version CAS | Good perf | Retry storms endgame | OK with backoff |
| CRDT merge bids | Available | Fairness hell | Bad for money |
| Global bids Kafka unordered | Scale | Ordering per auction hard | Need partition=auction_id |

**Chosen:** Kafka (or log) **partition key = auction_id** + **single consumer thread / actor** applying bids to durable state (DB/Rocks) **or** OLTP with version CAS + short retry.

**Deal-breaker:** concurrent unsynchronized read-modify-write on `current_price` across many app servers.

### 3.5 Soft-close rules

```text
if bid.accepted and now >= end_ts - window:
  end_ts = min(end_ts + extend_by, hard_cap_end)
emit AuctionExtended
```

Server clock only. Publish extensions on live channel.

### 3.6 Proxy bidding

```text
on max_bid from user:
  store proxy.max
  while true:
    needed = current + increment
    if user already leader: break
    if proxy.max < needed: break
    place system bid at needed for user (ledger)
    resolve against other proxies (highest max wins, price = second+inc)
```

Classic proxy rules — document carefully in interview.

### 3.7 Realtime — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Poll 1s | Simple | Load |
| WS per auction | Good UX | Fanout |
| SSE | Fine | Uni |

**Chosen:** WS/SSE with **coalesced** `PriceTick` events; state also on GET for refresh.

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Correctness | Per-auction serial apply | Money fairness | Unlocked concurrent updates |
| Isolation | Auction cell ≠ feed | Blast radius | Bids in core feed DB |
| Live | Coalesced ticks | Watcher amp | Per-bid full history push |
| Payments | Async settlement workflow | PSP latency | Sync capture on every bid |
| Time | Server end_ts | Fairness | Trust client clocks |
| Ads vs product | Separate systems | Different SLOs | Designing ads exchange by mistake |
| Inventory | Hard hold on list | Double-sell | Soft “hope” no hold |
| Proxy | Second-price style rules | UX fairness | First-price only undocumented |
| Soft-close | Extend + hard cap | Anti-snipe | Fixed end with last-ms snipes only |
| Fraud | Sync light + async heavy | Latency vs safety | Block all bids on slow ML |

**Expanded deal-breakers:**

1. **Unlocked RMW on current_price** — lost updates; wrong winner.  
2. **Ads auction mental model** — RTB is milliseconds × millions QPS; product auctions are correctness/money.  
3. **Capture payment on every bid** — PSP latency kills UX; auth/hold ≠ capture.  
4. **No inventory hold** — same SKU sold twice across listings.  
5. **Client-clock end time** — sniping/cheating disputes.

---

## 4. Architecture Diagram

```text
 IG App / Web
     |
     | HTTPS + WSS
     v
 +--------------------+      +------------------+
 | Auction API        |----->| Live Gateway     |
 +---------+----------+      +--------+---------+
           |                          ^
           v                          |
 +---------+----------+               |
 | Bid Engine         |--+ coalesced ticks
 | (per auction serial)|  |
 +---------+----------+  |
           |             |
           v             |
 +---------+---+   +-----+-----------+
 | Auction OLTP|   | Bid Log (Kafka/ |
 | state+CAS   |   | append store)   |
 +---------+---+   +------+----------+
           |              |
           v              v
 +----------------+  +----------------+
 | Settlement WF  |  | Risk / Fraud   |
 | Payments hooks |  |                |
 +----------------+  +----------------+
           |
           v
      Notif + Commerce fulfillment outbox

 Closer / Scheduler workers: transition LIVE->ENDED at end_ts
```

**Place bid path:**

```text
POST /bids (Idempotency-Key)
  -> auth, geo, risk pre-check
  -> enqueue/apply on auction actor
  -> validate LIVE, amount, increment
  -> append bid log
  -> update state (price, leader, maybe extend)
  -> ACK BidResult
  -> async: live tick, notif outbid, metrics
```

**Close path:**

```text
Closer wakes at end_ts (or event)
  -> ensure no in-flight bids (drain)
  -> state ENDING -> ENDED
  -> compute winner (or none)
  -> start settlement workflow
```

**Settlement path:**

```text
create payment intent for winner
  await pay / timeout
  on fail: offer next bidder
  on success: mark PAID; outbox fulfill
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Bid accepted ⇒ durable in bid log** with monotonic `bid_seq` per auction.  
2. **Winner determined only from log + rules** (recomputable).  
3. **Idempotent bid API**.  
4. **Server authoritative time**.  
5. **Settlement steps idempotent** (workflow keys).  
6. **Feed outage ≠ bid corruption** (isolation).

#### 5.1.2 Exactly-once money?

Aim for **exactly-once settlement effects** via idempotent payment keys; bids are **at-least-once applied** with idempotency keys.

#### 5.1.3 Failure modes

| Failure | Mitigation |
|---------|------------|
| Engine node dies | Replay log from last snapshot; same auction_id ownership |
| Double settlement | Idempotency keys to Payments |
| Live fanout down | Clients poll GET state |
| Clock on worker skew | NTP + end_ts from store; not worker local alone |
| Risk service down | Fail closed for high amount; fail open small with review — product choice explicit |

#### 5.1.4 Recomputing winner

```text
replay bid_log in seq order with rules
=> current_price, leader, end_ts extensions
must match stored state (checksum audit)
```

### 5.2 Scalability

#### 5.2.1 Partitioning

| Entity | Key |
|--------|-----|
| Auction state | `auction_id` |
| Bid log | `auction_id` (ordered) |
| User bid history | `user_id` secondary |
| Live interest | `auction_id` |

Never require cross-auction transactions in MVP.

#### 5.2.2 Endgame load

Pre-warm:

- Cache auction state at edge with very short TTL or versioned push.  
- Scale live gateways for watchers.  
- Engine single-writer still OK at few K bids/s; if extreme, optimize in-process.

#### 5.2.3 Progressive scale

| Scale | Strategy |
|-------|----------|
| Baseline | OLTP CAS + Redis live |
| 10× | Kafka per-auction partitions + actors |
| 100× | Auction cells by id range; risk platform |
| 1,000× | Edge ticks; specialized hot auction hosts |

### 5.3 Maintainability

#### 5.3.1 Isolation from IG core

| Concern | Approach |
|---------|----------|
| DB | Separate auction cluster |
| Deploy | Separate service |
| Failure | Feature flag disable create; running auctions continue if possible |
| Media | Reference media_id only |

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| Bid apply latency | SLO |
| Reject reasons | UX/fraud |
| Extension counts | Anti-snipe health |
| Settlement success % | Revenue trust |
| State vs log divergence | Correctness |
| Watcher count / auction | Fanout planning |

#### 5.3.3 Dispute tooling

Admin can reconstruct auction from bid log; export for trust & safety.

### 5.4 Fraud & trust

| Signal | Use |
|--------|-----|
| New account / stolen payment | Hold settlement |
| Shill (seller collusion) | Graph + device |
| Bid retract spam | Policy limited retract |
| Price manipulation | Anomaly on increments |

### 5.5 Proxy bid fairness

Document:

- Highest max wins.  
- Winning price = second_max + increment (or start).  
- Ties broken by earlier max placement time.

### 5.6 Privacy

- Leader identity may be masked (“User****”) until end.  
- Bid amounts public for transparency or only current price — product decision; state explicitly.

### 5.7 Legal / geo

```text
auction.allowed_regions
bid path checks user geo
payments compliance KYC on seller
```

### 5.8 Inventory hold deep dive

#### 5.8.1 Hold lifecycle

```text
LIST/SCHEDULED: create hold(item_id, auction_id, qty=1)
LIVE/ENDING: hold active
ENDED sold: convert hold → sale reservation → settlement
ENDED unsold / void: release hold
Cancel before LIVE: release if policy allows
```

#### 5.8.2 Double-list prevention

```text
Hold service unique constraint on item_id for active holds
Or conditional: only one LIVE auction per item
Media/IG shop item reference validated at create
```

#### 5.8.3 Failure

If settlement fails after END: keep reservation; retry capture; do not release to another auction until terminal fail + ops.

### 5.9 Bid path deep dive

#### 5.9.1 Apply steps (serial)

```text
1. Load auction state (must LIVE/ENDING)
2. Check end_ts vs server_now (soft-close may extend)
3. Validate amount ≥ min_next; currency; bidder ≠ seller
4. Risk soft gate
5. Apply proxy logic if max bid
6. Append immutable BidLog entry
7. Update state {leader, price, end_ts, version}
8. ACK BidAccepted | BidRejected
9. Emit events for live/notif
```

#### 5.9.2 Idempotency

```text
idempotency_key unique per bidder
Retry returns original accept/reject
Different body same key → conflict
```

#### 5.9.3 Ordering

All bids for `auction_id` on one ordered log/actor — **total order** defines fairness.

### 5.10 Fairness deep dive

#### 5.10.1 Proxy / second price

```text
Winner: highest max
Price: max(start, second_max + increment)
Tie: earlier proxy timestamp wins
Public display: current price not necessarily winner's max
```

#### 5.10.2 Soft-close fairness

```text
Snipes extend end; hard_cap prevents infinite
Document max extensions
All bidders see AuctionExtended with new end_ts
```

#### 5.10.3 Transparency

Bid history visible (masked identities optional); disputes reconstruct from log hashes.

### 5.11 Payment & settlement deep dive

#### 5.11.1 Authorization vs capture

| Phase | When |
|-------|------|
| Optional pre-auth | High-value bidders / policy |
| Capture | On win at settlement |
| Refund/void | Failures / returns |

#### 5.11.2 Workflow

```text
on ENDED with winner:
  start SettlementWF(auction_id) idempotent
  → charge winner via Payments
  → mark PAID / FAILED
  → release/commit inventory
  → notify parties
  → payout seller (minus fees) async with KYC holds
```

#### 5.11.3 Exactly-once money

At-least-once WF with **idempotent capture keys**; ledger entries unique on `(auction_id, type)`.

### 5.12 Fraud deep dive

#### 5.12.1 Online gates

- Velocity bids / auctions  
- New account × high max  
- Seller–bidder graph collusion edges  
- Payment instrument risk  

#### 5.12.2 Shill bidding

```text
Detect seller-linked accounts bidding up price
Signals: device, payment, social graph, IP
Actions: freeze auction, void, account strikes
```

#### 5.12.3 Bid retract policy

Limited retract window; after threshold locked; abuse → ban from auctions.

### 5.13 Progressive scale (10× / 100× / 1,000×)

| Jump | Engine | Live | Money |
|------|--------|------|-------|
| →10× | Per-auction actors proven | Coalesce ticks | WF retries hardened |
| →100× | Cells by auction_id | Regional WS | Risk platform |
| →1,000× | Hot auction hosts | Edge ticks | Multi-PSP; ledger cells |

**Narrative:** correctness stays single-writer per auction; scale out by many auctions, not by parallel unsynchronized writers on one auction.

### 5.14 Failure drills

| Drill | Expected |
|-------|----------|
| Engine crash mid-bid | Log decide; idempotent retry safe |
| Soft-close clock skew | NTP; monotonic server time |
| PSP double callback | Idempotent settlement |
| Shill spike | Freeze + T&S queue |

### 5.15 End-to-end bid sequence (worked)

```text
t0  Bidder submits POST /bids {amount:120, idem:K1}
t1  Risk soft OK; actor loads state price=100 leader=A
t2  Validate min_next=110 → OK
t3  Append log #482; state price=120 leader=B version++
t4  ACK BidAccepted {price:120, end_ts}
t5  Coalesce → PriceTick to watchers at t0+150ms
t6  Notify previous leader A “outbid”
```

Proxy variant: bidder sends `max_amount:500`; engine may set displayed price to `second+inc` not 500.

### 5.16 Closer / ENDING state machine

```text
Closer (HA leader):
  wake at end_ts
  transition LIVE → ENDING (lock new high bids? or allow only in-flight)
  drain in-flight applies with cutoff = end_ts
  compute winner from state/log
  transition ENDED {winner, price, reason}
  enqueue SettlementWF
```

**Policy choice to state:** bids with server_receive_ts ≤ end_ts valid; in-flight after freeze rejected with `AUCTION_ENDED`.

### 5.17 Watcher & notification planes

| Plane | Latency SLO | Content |
|-------|-------------|---------|
| Live tick | <1s coalesced | price, end_ts, leader masked |
| Push notif | seconds | outbid, won, paid |
| Email/receipt | minutes | settlement |

Never put push provider RTT on bid ACK path.

### 5.18 Ads auction vs product auction (explicit)

| Dimension | Ads RTB | IG product auction |
|-----------|---------|-------------------|
| QPS | millions | thousands |
| Latency | <100ms budget whole auction | 100–200ms bid ACK OK |
| Value | expected $/impression | final sale price |
| Correctness | statistical OK | exact winner mandatory |
| Inventory | attention/slots | physical/digital goods hold |

**Say this early** so the interviewer doesn’t steer you into exchange design.

### 5.19 Progressive scale narrative (long form)

- **→10×:** Prove serial engine + soft-close + idempotent settlement under celebrity drops.  
- **→100×:** Shard auctions into cells; risk feature store; regional live gateways; still one writer per auction.  
- **→1,000×:** Hot-auction dedicated hosts; edge price ticks; multi-PSP; ledger/billing cells; T&S ML platform — API contracts stable.

### 5.20 Operator kill switches

| Switch | Effect |
|--------|--------|
| `disable_create` | No new listings; live auctions continue |
| `disable_bids` | Freeze bidding; preserve state |
| `force_extend` | Ops anti-incident tool (audited) |
| `freeze_settlement` | Hold payouts pending T&S |

Kill switches are config-as-data with audit logs — required for money systems.

---

## 6. Wrap-Up

### 6.1 Design summary

Instagram **product auctions** as an isolated system:

1. Auction state machine + **immutable bid log**.  
2. **Per-auction serial bid engine** with soft-close.  
3. Proxy bidding rules.  
4. Coalesced realtime ticks for watchers.  
5. Idempotent **settlement workflows** with Payments.  
6. Fraud/risk hooks; clear separation from **ads auction** and core feed.

### 6.2 Key tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Correctness vs distributed writes | Single-writer per auction |
| Live freshness vs amp | Coalesce ticks |
| Payment latency vs bid path | Async settlement after end |
| Transparency vs privacy | Mask bidder ids MVP |

### 6.3 Deal-breakers

- Unsynchronized price updates.  
- Trusting client end time.  
- Designing ads exchange instead.  
- Settling money only in Redis without ledger.  
- Coupling auction writes into IG feed primary DB.

### 6.4 30-minute checklist

1. Clarify English auction, soft-close, payments, not ads.  
2. Estimate bids/s vs watchers → coalesce.  
3. Draw API → serial engine → log → settlement.  
4. Proxy + close rules.  
5. Isolation + fraud.  
6. Scale jumps.  
7. Deal-breakers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product clarity

**Q1: How is this different from ads auction?**  
A: Ads: continuous clearing, CTR/value models, millions QPS. Product: human timed lots, ledger, payments, fewer QPS, stronger per-item fairness UX.

**Q2: Why Instagram not a separate app?**  
A: Distribution via posts/stories; reuse identity/checkout — still isolate backend.

**Q3: Reserve price visible?**  
A: Product choice; often hidden until met.

**Q4: Buy Now + auction?**  
A: Parallel offer ends auction early if purchased — state transition careful.

**Q5: Charity auctions?**  
A: Same engine; different settlement split / compliance.

### 7.2 Correctness

**Q6: Why per-auction serialization?**  
A: Total order of bids makes winner unique and explainable.

**Q7: How does idempotency work?**  
A: `(bidder_id, idempotency_key)` unique; return original result.

**Q8: Can two leaders exist?**  
A: No — engine ownership via partition or DB constraint on version.

**Q9: Recompute from log?**  
A: Yes — audit and repair foundation.

**Q10: What if closer runs twice?**  
A: Idempotent ENDED transition; settlement workflow id stable.

### 7.3 Soft-close & time

**Q11: Why soft-close?**  
A: Reduce sniping unfairness; improve price discovery.

**Q12: Unbounded extensions?**  
A: Cap extensions or hard_cap_end.

**Q13: Client countdown drift?**  
A: Sync `server_now` + `end_ts`; periodic correction.

**Q14: Bid in flight at end?**  
A: Drain window; bid with server_receive_ts ≤ end_ts accepted.

**Q15: Whose clock for receive_ts?**  
A: Engine server / append log timestamp.

### 7.4 Proxy bidding

**Q16: Explain second-price style with proxies.**  
A: Highest max wins; price = second + increment; system places intermediate bids.

**Q17: Does proxy create many ledger rows?**  
A: Yes — each system bid logged for audit; may coalesce display.

**Q18: User lowers max below current?**  
A: Reject or allow only above current+inc; never retroactive unfairness.

**Q19: Two equal max?**  
A: Earlier proxy wins; price = max (or +0).

**Q20: Proxy vs manual only MVP?**  
A: Manual only simplifies; proxy is common — ask interviewer.

### 7.5 Realtime & scale

**Q21: Watcher fanout strategy?**  
A: Hierarchical pub/sub; coalesce PriceTick 100–200ms.

**Q22: Do we stream every bid to mobile?**  
A: Not necessarily — current price + occasional bid toast enough.

**Q23: Hot auction host?**  
A: Pin actor to dedicated workers near end; pre-warm caches.

**Q24: Read scalability for GET?**  
A: Versioned cache; invalidate on state version++.

**Q25: Cross-region bidding?**  
A: Home auction in one region; remote users higher latency; strong consistency home.

### 7.6 Payments & settlement

**Q26: Authorize on each bid?**  
A: Usually not — authorize/capture on win (or soft pre-auth product-dependent).

**Q27: Winner doesn’t pay?**  
A: Timeout → next bidder offer; reputation penalty.

**Q28: Idempotent capture?**  
A: `settlement_id` as payment idempotency key.

**Q29: Refunds?**  
A: Ledger + payments refund API; state REFUNDED.

**Q30: Partial inventory?**  
A: MVP single-unit lots; multi-unit is different algorithm.

### 7.7 Fraud & trust

**Q31: Shill bidding?**  
A: Detect seller-linked accounts; device graphs; freeze funds.

**Q32: Bot snipers?**  
A: Rate limits; soft-close; device trust; not perfect.

**Q33: Money laundering?**  
A: Payments compliance; velocity; KYC sellers.

**Q34: Fake listings?**  
A: Seller verification; media moderation; takedowns.

**Q35: Dispute after pay?**  
A: Commerce dispute flow; freeze fulfillment.

### 7.8 Alternatives & craft

**Q36: Store bids only in Redis?**  
A: OK for ephemeral UI; **not** system of record for money.

**Q37: SQL `UPDATE auctions SET price WHERE price < ?`?**  
A: Valid MVP serialization technique if contended carefully; still need bid log.

**Q38: Smart contracts on chain?**  
A: Out of scope; different trust model.

**Q39: How to open interview?**  
A: “Not ads auction” → type English timed → soft-close → payments → scale of watchers vs bids.

**Q40: L5+ impress?**  
A: Log-recomputable winner, soft-close caps, proxy rules, settlement idempotency, isolation, fanout coalesce.

**Q41: Common mistake?**  
A: Jumping into Kafka microservices without per-auction ordering; or ads confusion.

**Q42: Multi-currency?**  
A: Single currency per auction MVP; FX elsewhere.

**Q43: Notifications storm at end?**  
A: Batch; prioritize winner/outbid; suppress spam.

**Q44: Integration with IG Live?**  
A: Live shopping overlay same engine; chat remains comments system.

**Q45: Metrics for fairness?**  
A: Extension distributions, last-second bid rates, dispute rates, settlement success.

---

### Appendix A — Bid apply pseudocode

```text
def apply_bid(a, bid):
  assert a.state == LIVE
  assert bid.amount >= a.current_price + a.increment
  assert bid.currency == a.currency
  append_log(bid)
  a.current_price = bid.amount
  a.leader = bid.bidder_id
  a.version += 1
  maybe_extend(a, bid)
  return Ack(a)
```

### Appendix B — Soft close

```text
def maybe_extend(a, bid):
  if bid.ts >= a.end_ts - a.window:
    a.end_ts = min(a.end_ts + a.extend, a.hard_cap)
```

### Appendix C — Close

```text
def close(a):
  drain_inflight(a.id)
  a.state = ENDED
  if a.current_price >= a.reserve:
    start_settlement(a, a.leader)
  else:
    a.state = ENDED_NO_WINNER
```

### Appendix D — Settlement WF

```text
states: OFFERED -> AUTHORIZED -> CAPTURED -> FULFILL
on timeout: OFFER_NEXT(second)
idempotency_key = settlement_id
```

### Appendix E — Event types

```text
BidAccepted, AuctionExtended, PriceTick,
AuctionEnded, SettlementUpdated, Outbid
```

### Appendix F — NFR card

```text
Bid p99 < 400ms
Per-auction serial
Server time
Ledger immutable
Payments idempotent
Isolated from feed
```

### Appendix G — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Actors + live coalesce |
| 100× | Cells + risk |
| 1,000× | Edge ticks + hot hosts |

### Appendix H — Reject reasons

```text
TOO_LOW, ENDED, NOT_LIVE, CURRENCY,
RATE_LIMIT, RISK_HOLD, IDEMPOTENT_REPLAY
```

### Appendix I — Masking

```text
leader_display = pseudonym until ENDED
history may show amounts only
```

### Appendix J — Worked example

```text
Peak 200 bids/s one auction
Actor loop ~0.5ms/bid => 2000/s capacity OK
50K watchers; ticks @ 5/s => 250K msgs/s with hierarchy OK-ish; coalesce more if needed
```

### Appendix K — CAS alternative

```text
UPDATE auctions
SET price=$amt, leader=$u, ver=ver+1, end_ts=$e
WHERE id=$id AND ver=$ver AND state='LIVE' AND price < $amt - inc + inc
```

### Appendix L — Outbox

```text
txn: update settlement; insert outbox(fulfill)
relay to commerce
```

### Appendix M — Risk checks

| Stage | Check |
|-------|-------|
| Bid | velocity, bans |
| Settlement | payment risk |
| Seller | KYC, content |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| Soft-close | End extension anti-snipe |
| Proxy bid | Max commission bidding |
| Bid seq | Per-auction order |
| Settlement | Pay after win |
| Hard cap | Max end time |

### Appendix O — Ads vs product table

| | Ads auction | Product auction |
|--|-------------|-----------------|
| Frequency | Continuous | Timed lot |
| QPS | Extreme | Moderate |
| UX | Hidden | Visible countdown |
| Money | Advertiser | Buyer/seller |

### Appendix P — Failure drill

| Drill | Expect |
|-------|--------|
| Kill engine mid-bid | Replay idempotent |
| Payments 500 | Retry idempotent |
| Live down | Poll GET |
| Extension storm | Cap |

### Appendix Q — Data retention

```text
Bid logs: years (legal)
Live ticks: ephemeral
Watch lists: until auction+TTL
```

### Appendix R — API errors

| Code | Meaning |
|------|---------|
| 409 | CAS / state conflict |
| 422 | Too low / invalid |
| 403 | Geo/policy |
| 429 | Rate |
| 504 | Engine overload |

### Appendix S — Proxy sketch

```text
def resolve_proxies(a):
  # highest max among non-leaders challenges leader
  ...
```

### Appendix T — Isolation checklist

```text
separate DB?
separate deploy?
feature flag?
no feed join on bid path?
```

### Appendix U — Closer design

```text
heap of auctions by end_ts
wake near end
re-read state (extensions may move end)
loop until stable ended
```

### Appendix V — 30m checklist compact

```text
Not-ads → Rules → Serial engine+log → Soft-close
→ Live coalesce → Settlement → Scale → Deal-breakers
```

---

*End of Instagram Auction Feature system design.*
