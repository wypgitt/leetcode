#!/usr/bin/env python3
"""Write gold-style CIDR + Chat Deletion LLD docs (no filler appendices)."""

from __future__ import annotations

from pathlib import Path

from _gold_lld_common import footer, header, qa_block

OUT = Path(__file__).parent


def cidr_doc() -> str:
    parts: list[str] = [
        header(
            "IPv4 CIDR Firewall Rule Matcher",
            "Longest-prefix match · Binary trie + sorted-list alt · Allow/deny · Default action · Snapshot swap",
            "Deterministic LPM; explicit default action; overlapping rules resolved by longest prefix; lock-free match via immutable snapshot",
        ),
        """
## 1. Clarify Requirements (Interview Q&A)

Goal: Design an **IPv4 CIDR firewall matcher** that accepts allow/deny rules, resolves **overlapping CIDR blocks** via **longest-prefix match (LPM)**, and exposes `match(ip)` returning `ALLOW` or `DENY`. Support **dynamic rule updates** without blocking concurrent readers using **snapshot swap**.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Scope | Single-process matcher library | Stateful firewall appliance, NAT, stateful TCP tracking |
| Rules | CIDR + ALLOW/DENY action | Layer-7 hostnames, port ranges (Phase 2) |
| Match semantics | LPM on 32-bit IPv4 | IPv6 (Phase 2), geo-IP |
| Updates | addRule/removeRule with snapshot publish | Distributed consensus across nodes |
| Databricks lens | Workspace IP allowlists, cluster ingress policy | Full SDN controller |

### 1.1 Clarifying questions (ask first)

| # | Question | Typical answer | Design impact |
|---|----------|----------------|---------------|
| F1 | Input IP format? | Dotted quad string `"10.0.1.5"` or `uint32` BE | Normalize once at boundary |
| F2 | Rule input? | `"10.0.0.0/8"` + action | Parse + validate prefix 0–32 |
| F3 | Overlapping rules? | **Longest prefix wins** | Trie walk tracks best-so-far |
| F4 | Same prefix, two rules? | **Last insert wins** (document tie-break) | Store `ruleSeq` on node |
| F5 | No matching rule? | Return configured **default action** (usually DENY) | Constructor param |
| F6 | Primary structure? | **Binary trie** MVP; sorted list acceptable for small N | State tradeoff on board |
| F7 | Concurrent updates? | Many readers, occasional writer | **Immutable snapshot + atomic swap** |
| F8 | removeRule? | Yes, by normalized CIDR key | Clear node action if present |
| F9 | Invalid inputs? | Throw at add/match boundary | Never insert malformed CIDR |
| F10 | `0.0.0.0/0`? | Valid catch-all, lowest specificity unless only rule | Works with LPM |
| F11 | Host routes `/32`? | Supported | Full 32-bit walk |
| F12 | Batch match? | Out of MVP | Single IP per call |

### 1.2 MVP scope (repeat back)

1. Parse and **normalize** IPv4 + CIDR → `(network uint32, prefixLen)`.
2. Store rules in a **binary trie** (primary) with sorted-list alternative documented.
3. `match(ip)`: walk trie, return action of **longest matching prefix**; else default.
4. `addRule` / `removeRule`: build **new immutable trie**, atomic pointer swap.
5. Overlap: longer prefix wins; equal prefix → last inserted wins.

**Out of MVP:** IPv6, Patricia compression, distributed rule sync, metrics export.

### 1.3 Core invariants (state early)

```text
I1  match(ip) returns action of the matching rule with MAXIMUM prefixLen.
I2  If two rules share the same prefixLen and both match ip, the rule with
    higher insertSeq (last added) wins.
I3  If no rule matches ip, return defaultAction (never null/undefined).
I4  All stored networks are normalized: network == (network & mask(prefixLen)).
I5  match() is read-only and thread-safe via volatile AtomicReference<BinaryTrie>.
I6  Updates publish a fully built new trie before swap — readers never see partial state.
```

---

## 2. APIs & Guarantees

### 2.1 Public surface

```java
enum Action { ALLOW, DENY }

public final class CidrFirewall implements AutoCloseable {
  public CidrFirewall(Action defaultAction);

  /** Validates CIDR, normalizes network, inserts into next snapshot. */
  public void addRule(String cidr, Action action) throws InvalidCidrException;

  /** Removes rule at exact normalized prefix; no-op if absent. */
  public void removeRule(String cidr) throws InvalidCidrException;

  /** Parse dotted-quad, return LPM action or default. */
  public Action match(String ip) throws InvalidIpException;

  /** Fast path when caller already parsed to uint32 big-endian. */
  public Action matchUint32(int ipBE);

  public int ruleCount();
  public Action defaultAction();
  public void close(); // optional: reject further updates
}

public final class Rule {
  public final int network;      // normalized, upper bits aligned
  public final int prefixLen;    // 0..32
  public final Action action;
  public final long ruleId;      // monotonic id for debugging
  public final long insertSeq;   // tie-break for same prefixLen
}
```

### 2.2 Internal package-private types

```java
final class CidrParser {
  static int parseIpv4(String s) throws InvalidIpException;
  static ParsedCidr parseCidr(String cidr) throws InvalidCidrException;
}

record ParsedCidr(int network, int prefixLen) {}

final class BinaryTrie {
  Action lpm(int ipBE);
  BinaryTrie insert(ParsedCidr cidr, Action action, long insertSeq);
  BinaryTrie remove(ParsedCidr cidr);
  int ruleCount();
}

final class TrieNode {
  TrieNode child0;  // immutable after publish
  TrieNode child1;
  Action action;    // null if no rule terminates here
  int prefixLen;    // -1 if no rule
  long insertSeq;   // tie-break
}

final class SortedRuleMatcher {
  Action lpm(int ipBE, List<Rule> rulesSortedDesc, Action defaultAction);
}

final class FirewallSnapshot {
  final BinaryTrie trie;
  final long version;  // bumped each swap
}
```

### 2.3 Guarantees

| Property | Guarantee |
|----------|-----------|
| LPM correctness | Most specific matching prefix always wins |
| Deterministic ties | Same prefixLen → highest insertSeq wins |
| Default action | Returned iff zero rules match |
| Parse safety | Invalid CIDR/IP rejected before mutation |
| Reader isolation | match() never blocks on add/remove |
| Atomic visibility | After swap, all threads see new trie or old trie entirely |
| Idempotent remove | Second remove same CIDR is no-op |

### 2.4 Error model

| Exception | When |
|-----------|------|
| `InvalidCidrException` | Bad format, octet > 255, prefixLen > 32, empty string |
| `InvalidIpException` | Malformed dotted quad at match time |
| `FirewallClosedException` | add/remove after close() |
| `RuleNotFoundException` | Optional strict remove API variant |

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility matrix

| Class | Owns | Does not |
|-------|------|----------|
| `CidrFirewall` | `AtomicReference<BinaryTrie>`, `defaultAction`, `insertSeq` counter | Bit manipulation details |
| `CidrParser` | String → uint32, mask math | Storage |
| `BinaryTrie` | Immutable tree of `TrieNode` | Concurrency (pure FP-ish copies) |
| `TrieNode` | One bit level, optional terminal rule | Mutable children post-publish |
| `SortedRuleMatcher` | O(n) scan reference impl / small-N path | Dynamic updates |
| `FirewallSnapshot` | Version metadata for tests | — |

### 3.2 ASCII component diagram

```text
                    ┌─────────────────────────────────────┐
                    │           CidrFirewall              │
                    │  defaultAction: Action              │
                    │  nextInsertSeq: AtomicLong          │
                    │  trieRef: AtomicReference<BinaryTrie>│
                    └───────────┬─────────────────────────┘
                                │
           addRule/removeRule   │   match(ip)
                    ┌───────────▼───────────┐
                    │  read trieRef.get()   │  (lock-free)
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │      BinaryTrie       │
                    │  root: TrieNode       │
                    │  lpm(ipBE) -> Action  │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
     ┌────────▼────────┐                 ┌────────▼────────┐
     │    TrieNode     │                 │   CidrParser    │
     │ child0, child1  │                 │ parseIpv4       │
     │ action?, len    │                 │ parseCidr+mask  │
     └─────────────────┘                 └─────────────────┘

Update path (writer):
  old = trieRef.get()
  next = old.insert(...) or old.remove(...)   // pure copy-on-write
  trieRef.set(next)                             // publish
```

### 3.3 Why immutable trie + swap (interview talking point)

Mutable trie under `ReadWriteLock` works but:
- Readers take read lock → writer starvation risk at high QPS.
- Harder to prove readers never observe torn tree.

**Snapshot swap:** writer builds fresh trie off-thread or under `updateLock`, then one atomic store. match() is a single volatile read + O(32) walk — no locks on hot path.

---

## 4. Core Data Structures & Algorithms

### 4.1 IPv4 representation

Store IPv4 as **32-bit unsigned int in big-endian bit order** (MSB = bit 0 of address):

```text
"10.0.1.5" → (10<<24)|(0<<16)|(1<<8)|5 = 0x0A000105

bit(ip, i) = (ip >>> (31 - i)) & 1     // i ∈ [0,31], i=0 is first bit of octet 1
```

Using unsigned shift avoids sign-extension bugs in Java/C#.

### 4.2 CIDR normalization

```text
mask(prefixLen):
  if prefixLen == 0: return 0
  return 0xFFFFFFFF << (32 - prefixLen)   // unsigned semantics

normalize(ip, prefixLen):
  return ip & mask(prefixLen)

parseCidr("10.1.2.3/24"):
  ip = parseIpv4("10.1.2.3")
  len = 24
  network = normalize(ip, 24)  → 0x0A010200
```

| Input CIDR | Normalized network | prefixLen |
|------------|-------------------|-----------|
| `10.1.2.3/24` | `10.1.2.0` | 24 |
| `10.1.2.0/24` | `10.1.2.0` | 24 |
| `0.0.0.0/0` | `0.0.0.0` | 0 |
| `192.168.1.1/32` | `192.168.1.1` | 32 |

**Interview tip:** Always normalize on insert so `removeRule("10.1.2.3/24")` hits the same node as `addRule("10.1.2.0/24", ...)`.

### 4.3 Membership test (sorted-list helper)

```text
matches(network, prefixLen, ip):
  return normalize(ip, prefixLen) == network
```

### 4.4 Binary trie — insert (copy-on-write)

Each insert returns a **new** trie sharing unchanged subtrees (path copying):

```text
insert(node, ip, prefixLen, action, insertSeq, depth):
  if depth == prefixLen:
    return node.withRule(action, prefixLen, insertSeq)  // new node copy
  b = bit(ip, depth)
  child = node.child[b]
  newChild = insert(child or EMPTY, ip, prefixLen, action, insertSeq, depth+1)
  return node.withChild(b, newChild)
```

Terminal node fields:
- `action != null` means a rule ends at this depth.
- Deeper nodes may still exist for longer prefixes.

### 4.5 Binary trie — LPM lookup

```text
lpm(root, ip):
  bestAction = null
  bestLen = -1
  bestSeq = -1
  node = root
  for depth in 0..31:
    if node.action != null:
      if node.prefixLen > bestLen OR
         (node.prefixLen == bestLen AND node.insertSeq > bestSeq):
        bestAction = node.action
        bestLen = node.prefixLen
        bestSeq = node.insertSeq
    b = bit(ip, depth)
    if node.child[b] == null: break
    node = node.child[b]
  return bestAction ?? defaultAction
```

**Why track at every node along path:** Rules can exist at `/8`, `/16`, `/24` on same path — must pick longest.

### 4.6 Worked LPM example

Rules (in insert order):

```text
R1: 10.0.0.0/8     DENY   insertSeq=1
R2: 10.0.1.0/24    ALLOW  insertSeq=2
R3: 10.0.1.0/24    DENY   insertSeq=3   // same prefix as R2 → R3 wins
R4: 10.0.1.5/32    ALLOW  insertSeq=4
```

| IP | Matching rules (prefixLen) | Winner | Result |
|----|---------------------------|--------|--------|
| `10.0.1.5` | /8, /24, /32 | /32 ALLOW | ALLOW |
| `10.0.1.99` | /8, /24 | /24 DENY (seq 3) | DENY |
| `10.2.0.1` | /8 only | /8 DENY | DENY |
| `8.8.8.8` | none | default | DENY (if default DENY) |

### 4.7 Sorted-list alternative

Maintain `List<Rule>` sorted by `(prefixLen DESC, insertSeq DESC)`.

```text
matchSorted(ip, rules, defaultAction):
  for r in rules:
    if matches(r.network, r.prefixLen, ip):
      return r.action
  return defaultAction
```

| Structure | match | add | remove | Space | When to choose |
|-----------|-------|-----|--------|-------|----------------|
| Binary trie | O(32) | O(32) copy path | O(32) | O(R·32) worst | Many rules, hot match path |
| Sorted list | O(R) | O(R log R) | O(R) | O(R) | R < ~50, interview simplicity |
| Radix tree (Patricia) | O(32) avg | O(32) | O(32) | Compressed | Sparse prefixes, Phase 2 |

**Interview script:** Start with sorted list for clarity, offer trie when interviewer scales to 100k rules.

### 4.8 removeRule on trie

```text
remove(node, ip, prefixLen, depth):
  if depth == prefixLen:
    return node.clearRule()   // action=null, prefixLen=-1; keep children
  b = bit(ip, depth)
  if node.child[b] == null: return node
  return node.withChild(b, remove(node.child[b], ip, prefixLen, depth+1))
```

Removing `/24` does **not** remove deeper `/32` rules — they remain valid LPM targets.

---

## 5. Concurrency Invariants & Race Analysis

### 5.1 Shared mutable state

| Field | Type | Access |
|-------|------|--------|
| `trieRef` | `AtomicReference<BinaryTrie>` | match: plain get; update: get→build→set |
| `nextInsertSeq` | `AtomicLong` | increment on each addRule |
| `defaultAction` | final | immutable |
| `updateLock` | `ReentrantLock` (optional) | serialize writers only |

### 5.2 Snapshot swap protocol

```text
addRule(cidr, action):
  parsed = CidrParser.parseCidr(cidr)
  seq = nextInsertSeq.incrementAndGet()
  updateLock.lock()
  try:
    old = trieRef.get()
    fresh = old.insert(parsed, action, seq)
    trieRef.set(fresh)           // linearization point for readers
  finally:
    updateLock.unlock()

match(ip):
  trie = trieRef.get()           // volatile read — no lock
  ipBE = CidrParser.parseIpv4(ip)
  return trie.lpm(ipBE, defaultAction)
```

Readers **never** take `updateLock`. Multiple writers serialized by `updateLock` prevents lost updates when two adds copy from same `old` base — alternative is CAS loop on `trieRef`.

### 5.3 CAS loop variant (lock-free writer coordination)

```text
addRuleCAS(cidr, action):
  parsed = ...
  seq = nextInsertSeq.incrementAndGet()
  loop:
    old = trieRef.get()
    fresh = old.insert(parsed, action, seq)
    if trieRef.compareAndSet(old, fresh): return
    // else retry — another writer published first
```

### 5.4 Race timeline A — match during add

```text
Time   Thread R (match)              Thread W (addRule)
────────────────────────────────────────────────────────────
t0                                   parse CIDR
t1     trieRef.get() → T0
t2                                   build T1 from T0
t3     lpm on T0 → DENY
t4                                   trieRef.set(T1)
t5     (done)                         (done)
t6     new match gets T1 → ALLOW
```

**Outcome:** R at t3 sees pre-add snapshot — correct, linearizable with serial order R before W.

### 5.5 Race timeline B — concurrent adds

```text
Time   Thread W1                       Thread W2
────────────────────────────────────────────────────────────
t0     old=T0                          old=T0
t1     build T0+R1                       build T0+R2
t2     set → T0+R1                      
t3                                     set → T0+R2  (LOST R1 if blind set!)
```

**Mitigation:** `updateLock` or CAS retry ensures W2 builds from T0+R1, producing T0+R1+R2.

### 5.6 Race timeline C — match never blocks

Unlike `ReadWriteLock`:
- No reader/writer lock coupling.
- match latency unaffected by slow add building large trie.

**Tradeoff:** addRule O(32) **copy** per update — acceptable for infrequent policy changes (seconds/minutes), not microsecond churn.

### 5.7 Invariants under concurrency

| ID | Invariant |
|----|-----------|
| C1 | `trieRef.get()` is never null after construction |
| C2 | Published trie instances are **immutable** — no post-set mutation |
| C3 | insertSeq strictly increases; tie-break is total order |
| C4 | match and matchUint32 are safe to call from unlimited threads |
| C5 | close() sets flag; subsequent add/remove throw (optional) |

---

## 6. Algorithms & Pseudocode

### 6.1 CidrParser.parseIpv4

```text
parseIpv4(s):
  if s == null or empty: throw InvalidIp
  parts = s.split("\\.")
  if parts.length != 4: throw InvalidIp
  result = 0
  for p in parts:
    if p empty or non-digit: throw InvalidIp
    octet = Integer.parseInt(p)
    if octet < 0 or octet > 255: throw InvalidIp
    result = (result << 8) | octet
  return result
```

### 6.2 CidrParser.parseCidr

```text
parseCidr(s):
  if s == null or !s.contains("/"): throw InvalidCidr
  idx = s.lastIndexOf('/')
  ipPart = s.substring(0, idx)
  lenPart = s.substring(idx + 1)
  ip = parseIpv4(ipPart)
  prefixLen = Integer.parseInt(lenPart)
  if prefixLen < 0 or prefixLen > 32: throw InvalidCidr
  network = ip & mask(prefixLen)
  return ParsedCidr(network, prefixLen)
```

### 6.3 CidrFirewall.addRule (full)

```text
addRule(cidr, action):
  checkNotClosed()
  parsed = CidrParser.parseCidr(cidr)
  seq = nextInsertSeq.incrementAndGet()
  updateLock.lock()
  try:
    current = trieRef.get()
    updated = current.insert(parsed.network, parsed.prefixLen, action, seq)
    trieRef.set(updated)
  finally:
    updateLock.unlock()
```

### 6.4 CidrFirewall.match

```text
match(ip):
  trie = trieRef.get()
  ipBE = CidrParser.parseIpv4(ip)
  result = trie.lpm(ipBE)
  return result != null ? result : defaultAction
```

### 6.5 BinaryTrie.insert (iterative sketch)

```text
insert(ip, prefixLen, action, insertSeq):
  return insertRec(EMPTY_NODE, ip, prefixLen, action, insertSeq, 0)

insertRec(node, ip, prefixLen, action, insertSeq, depth):
  if depth == prefixLen:
    return copyNode(node).setTerminal(action, prefixLen, insertSeq)
  b = bit(ip, depth)
  child = node.child[b]
  newChild = insertRec(child ?? EMPTY_NODE, ip, prefixLen, action, insertSeq, depth+1)
  return copyNode(node).setChild(b, newChild)
```

### 6.6 SortedRuleMatcher reference implementation

```text
class SortedRuleListFirewall:
  rules: List<Rule> = []
  defaultAction: Action

  addRule(cidr, action):
    parsed = parseCidr(cidr)
    seq = ++globalSeq
    rules.add(Rule(parsed, action, seq))
    rules.sort(by prefixLen DESC, insertSeq DESC)

  match(ip):
    ipBE = parseIpv4(ip)
    for r in rules:
      if matches(r.network, r.prefixLen, ipBE):
        return r.action
    return defaultAction
```

Use in tests as **oracle** to validate trie LPM correctness.

### 6.7 Default action semantics

```text
// Deny-by-default (secure):
fw = new CidrFirewall(Action.DENY)
fw.addRule("10.0.0.0/8", Action.ALLOW)
match("10.0.0.1") → ALLOW
match("8.8.8.8")  → DENY

// Allow-by-default (less common):
fw = new CidrFirewall(Action.ALLOW)
fw.addRule("203.0.113.0/24", Action.DENY)
match("203.0.113.50") → DENY
match("1.2.3.4")      → ALLOW
```

State explicitly in interview — wrong default is a security bug.

---

## 7. Failure Modes & Recovery

| Scenario | Symptom | Mitigation |
|----------|---------|------------|
| Unnormalized add | Duplicate `/24` keys | Always normalize in parseCidr |
| Endianness bug | Wrong match for known IPs | Golden tests with fixed uint32 |
| Lost concurrent update | Rule missing after parallel adds | updateLock or CAS retry |
| Trie memory growth | Many rules, sparse paths | Patricia compression Phase 2 |
| Same prefix flip-flop | ALLOW→DENY→ALLOW churn | Last insert wins by design |
| match on closed fw | Should still work read-only | Document: match OK, add throws |
| Invalid IP at match | Partial parse | All-or-nothing parseIpv4 |
| `10/8` shorthand | Parser reject | Require dotted quad MVP |

### 7.1 Recovery after bad deploy

Policy files are typically rebuilt from source of truth (Terraform, config service):

```text
1. Load rules into new BinaryTrie off-line
2. AtomicReference.set(newTrie) — instant cutover
3. Roll back = swap previous snapshot retained (keep last N versions Phase 2)
```

No partial recovery needed — trie is derived state.

---

## 8. Tests & Edge Cases

### 8.1 Unit tests — parsing

```java
@Test void normalizeEquivalentCidrs() {
  var a = parseCidr("10.1.2.3/24");
  var b = parseCidr("10.1.2.0/24");
  assertEquals(a, b);
}

@Test void rejectBadPrefix() {
  assertThrows(InvalidCidrException.class, () -> parseCidr("10.0.0.0/33"));
}

@Test void rejectOctet256() {
  assertThrows(InvalidIpException.class, () -> parseIpv4("256.0.0.1"));
}
```

### 8.2 Unit tests — LPM correctness

```java
@Test void longestPrefixWins() {
  fw.addRule("10.0.0.0/8", DENY);
  fw.addRule("10.0.1.0/24", ALLOW);
  assertEquals(ALLOW, fw.match("10.0.1.5"));
  assertEquals(DENY, fw.match("10.0.2.1"));
}

@Test void samePrefixLastWins() {
  fw.addRule("10.0.0.0/8", ALLOW);
  fw.addRule("10.0.0.0/8", DENY);
  assertEquals(DENY, fw.match("10.0.0.1"));
}

@Test void defaultWhenNoMatch() {
  assertEquals(DENY, fw.match("8.8.8.8"));
}

@Test void hostRoute32() {
  fw.addRule("192.168.1.1/32", ALLOW);
  assertEquals(ALLOW, fw.match("192.168.1.1"));
  assertEquals(DENY, fw.match("192.168.1.2"));
}

@Test void catchAllZeroPrefix() {
  fw.addRule("0.0.0.0/0", ALLOW);
  assertEquals(ALLOW, fw.match("1.2.3.4"));
}
```

### 8.3 Property test — trie vs sorted oracle

```java
@RepeatedTest(200)
void trieMatchesSortedOracle() {
  Random rnd = new Random(seed);
  buildRandomRules(trieFw, sortedFw, rnd, 30);
  for (int i = 0; i < 100; i++) {
    String ip = randomIp(rnd);
    assertEquals(sortedFw.match(ip), trieFw.match(ip));
  }
}
```

### 8.4 Concurrency tests

```java
@Test void concurrentMatchDuringAdd() throws Exception {
  ExecutorService ex = Executors.newFixedThreadPool(20);
  CountDownLatch start = new CountDownLatch(1);
  for (int i = 0; i < 10000; i++) {
    ex.submit(() -> {
      start.await();
      Action a = fw.match("10.0.0.1");
      assertTrue(a == ALLOW || a == DENY); // never crash or null
    });
  }
  ex.submit(() -> { start.await(); fw.addRule("10.0.0.0/8", ALLOW); });
  start.countDown();
  ex.shutdown();
  assertTrue(ex.awaitTermination(30, SECONDS));
}

@Test void concurrentAddsAllPresent() {
  // 50 threads each add distinct /32 → ruleCount == 50
}
```

### 8.5 removeRule tests

```java
@Test void removeDoesNotAffectLongerPrefix() {
  fw.addRule("10.0.0.0/8", DENY);
  fw.addRule("10.0.1.0/24", ALLOW);
  fw.removeRule("10.0.0.0/8");
  assertEquals(ALLOW, fw.match("10.0.1.1"));
  assertEquals(DENY, fw.match("10.0.2.1")); // falls to default
}
```

---

## 9. Complexity & Scalability Notes

### 9.1 Single-node complexity

| Operation | Binary trie | Sorted list |
|-----------|-------------|-------------|
| match | O(32) = O(1) | O(R) |
| addRule | O(32) path copy | O(R log R) |
| removeRule | O(32) | O(R) |
| Space | O(R · 32) nodes worst case | O(R) |

R = number of rules.

### 9.2 When snapshot copy is too expensive

If updates exceed ~100/sec with millions of rules:
- **Double-buffered mutable trie** under RWLock (faster writes, lock on read).
- **Incremental persistent trie** (COW pages).
- Push rules to **hardware TCAM** / kernel eBPF map — mention for scale story.

### 9.3 Databricks context

Workspace IP access lists and cluster ingress policies are **read-heavy, write-rare** — snapshot swap is ideal. Policy change propagates in one atomic flip; running queries see consistent allow/deny for entire request.

---

## 10. Wrap-Up

**Deliverables on whiteboard**

1. `CidrParser` normalize + validate
2. `BinaryTrie.lpm` with bestLen/bestSeq tracking
3. `CidrFirewall` with `AtomicReference` snapshot swap
4. Sorted-list oracle for testing
5. Default action stated explicitly

**MVP vs Phase 2**

| MVP | Phase 2 |
|-----|---------|
| IPv4 trie + swap | IPv6 128-bit |
| Last-wins same prefix | Explicit conflict API |
| In-memory | Versioned rollback stack |

**Top mistakes to avoid**

1. First matching rule in list order (not LPM)
2. Forgetting to normalize CIDR on insert/remove
3. Mutable trie shared without synchronization
4. Signed shift bugs in bit extraction

---
""",
        qa_block([
            (
                "Why longest-prefix match instead of first rule wins?",
                "Overlapping CIDR blocks are common (`10/8` deny, `10.0.1/24` allow). "
                "First-wins depends on insertion order and is error-prone. LPM matches "
                "BGP routing semantics and gives deterministic, most-specific intent.",
            ),
            (
                "Trie vs sorted list — what do you say in 30 seconds?",
                "Sorted list: sort rules by prefix length descending, scan until first match — "
                "O(n) match, simple to code. Binary trie: walk 32 bits, track best terminal node — "
                "O(1) match. For interview MVP with <50 rules, list is fine; for production "
                "firewalls with 100k+ rules, trie or compressed radix tree.",
            ),
            (
                "How do you handle concurrent addRule and match?",
                "Immutable trie + AtomicReference snapshot swap. match() does volatile get "
                "and pure read-only walk — no locks. addRule copies path into new trie, "
                "then publishes with set/CAS. Readers see old or new trie entirely, never torn.",
            ),
            (
                "Same prefix added twice with different actions?",
                "Document **last insert wins** via monotonic insertSeq on the terminal node. "
                "Alternative policy: reject with ConflictException — ask interviewer preference.",
            ),
            (
                "What default action do you pick?",
                "**Deny-by-default** for security (implicit deny). Explicit allow rules only. "
                "Mention allow-by-default only if requirements say internal service mesh.",
            ),
            (
                "How do you test LPM without hand-writing 100 cases?",
                "Dual implementation: sorted-list oracle vs trie. Property-based random rule "
                "generation + random IPs; assert both matchers agree. Add known BGP-style "
                "overlap cases from section 4.6.",
            ),
            (
                "Does removeRule break longer prefixes?",
                "No — remove clears terminal at exact depth only. Child nodes for longer "
                "prefixes remain. Test: remove /8, keep /24, verify /24 still matches.",
            ),
            (
                "Endianness — what goes wrong?",
                "Using signed `>>` on Java int sign-extends high bit. Use `>>>` unsigned. "
                "Also be consistent: bit 0 = first octet MSB. Golden test: 10.0.0.1 → 0x0A000001.",
            ),
            (
                "Can match() ever return null?",
                "No — invariant I3. lpm returns null internally only when no terminal matched; "
                "public API substitutes defaultAction.",
            ),
        ]),
        """
## 12. Appendices

### A. Bit mask reference

```text
prefixLen  mask (hex)      host bits
0          0x00000000      32
8          0xFF000000      24
16         0xFFFF0000      16
24         0xFFFFFF00      8
32         0xFFFFFFFF      0
```

### B. Glossary

| Term | Meaning |
|------|---------|
| LPM | Longest-prefix match — most specific CIDR wins |
| CIDR | Classless Inter-Domain Routing block network/prefix |
| Snapshot swap | Atomic publish of immutable data structure |
| Terminal node | Trie node where a rule's prefix ends |
| insertSeq | Monotonic tie-breaker for same-length prefixes |

### C. Final checklist

- [ ] Normalize CIDR on every insert/remove
- [ ] LPM tracks bestLen + bestSeq at each depth
- [ ] defaultAction explicit (deny typical)
- [ ] match lock-free via AtomicReference
- [ ] Writers serialized (lock or CAS)
- [ ] Oracle test trie vs sorted list
- [ ] Golden IP parse tests (endianness)
""",
        footer(),
    ]
    return "\n".join(parts)


def chat_doc() -> str:
    parts: list[str] = [
        header(
            "Chat Conversation Delete vs Concurrent Sends",
            "Tombstone deleteSeq · Monotonic seq · Policy A reject-after-delete · Per-conversation lock · Race timelines",
            "Strict visibility: no message with seq ≤ deleteSeq after delete; send after delete rejected; races linearized per conversation",
        ),
        """
## 1. Clarify Requirements (Interview Q&A)

Goal: Design an in-memory **chat message store** supporting `send`, `deleteConversation`, and `listMessages`, where **global conversation delete** races with **concurrent sends**. Use **monotonic sequence numbers**, a **tombstone** with `deleteSeq`, and **Policy A** (reject send after delete commits).

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Scope | Single-node conversation store | Full Slack/WhatsApp product |
| Delete scope | Entire conversation tombstone | Per-message unsend (Phase 2) |
| Ordering | Per-conversation monotonic `seq` | Global cross-chat total order |
| Visibility | `seq > deleteSeq` on read | Hard GDPR erase (Phase 2) |
| Databricks lens | Metadata lifecycle, soft delete | Multi-region CRDT chat |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Delete granularity? | Whole conversation | One tombstone per conv |
| F2 | Sequence source? | Server assigns on commit | Client supplies body only |
| F3 | After delete, new send? | **Rejected** (Policy A) | Check tombstone under lock |
| F4 | Visibility rule? | `visible iff msg.seq > deleteSeq` | Filter on listMessages |
| F5 | deleteSeq value? | `maxSeq` at delete commit time | All committed msgs hidden |
| F6 | Concurrent ops? | Many sends + one delete | **Per-conversation lock** |
| F7 | Idempotent delete? | Second delete is no-op | Sticky tombstone |
| F8 | In-flight send before delete? | If delete wins lock first → send rejected | Document timeline |
| F9 | Read cursor? | `listMessages(afterSeq, limit)` | Skip seq ≤ deleteSeq |
| F10 | Durability? | In-memory MVP | WAL extension noted |
| F11 | deletedAt? | Audit timestamp | Not used for visibility |
| F12 | Resurrect conversation? | No (MVP) | Tombstone permanent |

### 1.2 MVP scope

1. `Conversation`: `TreeMap<Long,Message>`, `nextSeq`, `maxSeq`, tombstone fields.
2. `send`: acquire conv lock → if deleted throw → assign seq → store.
3. `deleteConversation`: lock → `deleteSeq = maxSeq`, `deleted = true`.
4. `listMessages`: lock → return msgs where `seq > deleteSeq` and `seq > afterSeq`.
5. **Policy A:** any send after tombstone set is rejected — no ghost messages.
6. Document race timelines for send vs delete interleaving.

### 1.3 Core invariants

```text
I1  For accepted sends, seq values are strictly increasing: 1, 2, 3, ...
I2  deleteSeq <= maxSeq always (equal at delete commit).
I3  After delete completes: deleted == true and deleteSeq == maxSeq at commit instant.
I4  listMessages never returns msg where msg.seq <= deleteSeq.
I5  send() after delete committed always throws ConversationDeletedException.
I6  All mutations on one conversation serialize through the same lock (linearizability).
I7  deleteConversation is idempotent: second call returns without changing deleteSeq.
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```java
public final class ChatStore implements AutoCloseable {
  public ChatStore();

  /** Assigns monotonic seq if conversation active; else throws. */
  public SendResult send(String conversationId, MessageDraft draft)
      throws ConversationDeletedException, NotFoundException;

  /** Tombstone: deleteSeq = maxSeq; idempotent. */
  public void deleteConversation(String conversationId) throws NotFoundException;

  /** Returns up to limit messages with seq > max(afterSeq, deleteSeq). */
  public List<Message> listMessages(String conversationId, long afterSeq, int limit)
      throws NotFoundException;

  public ConversationMeta getMeta(String conversationId) throws NotFoundException;

  public void close();
}

public record MessageDraft(String senderId, String body) {}

public record Message(long seq, String senderId, String body, Instant createdAt) {}

public record SendResult(long seq, boolean accepted) {}

public record ConversationMeta(
    boolean deleted,
    long deleteSeq,
    long maxSeq,
    Instant deletedAt
) {}
```

### 2.2 Internal types

```java
final class Conversation {
  final String id;
  final NavigableMap<Long, Message> messages = new TreeMap<>();
  long nextSeq = 1;       // next to assign
  long maxSeq = 0;        // highest assigned
  boolean deleted = false;
  long deleteSeq = 0;     // meaningful when deleted
  Instant deletedAt = null;
}

final class ConversationRegistry {
  ConcurrentHashMap<String, Conversation> map;
  Conversation getOrCreate(String id);
}

final class ConversationLockStriped {
  Lock lockFor(String conversationId);  // striped locks or lock in Conversation
}
```

### 2.3 Guarantees

| Property | Guarantee |
|----------|-----------|
| Per-conv linearizability | send/delete/list on same conv serialize |
| Seq monotonicity | Accepted sends get unique increasing seq |
| Delete atomicity | Tombstone appears atomically at lock release |
| Policy A | Post-delete sends never succeed |
| Read visibility | No seq ≤ deleteSeq returned after delete |
| Cross-conv parallelism | Different conversationIds do not block each other |
| Idempotent delete | Repeated delete is safe |

### 2.4 Error model

| Exception | When |
|-----------|------|
| `ConversationDeletedException` | send on tombstoned conversation |
| `NotFoundException` | Unknown conversationId (optional: auto-create on send) |
| `InvalidArgumentException` | Empty body, limit <= 0 |
| `StoreClosedException` | After close() |

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Role |
|-------|------|
| `ChatStore` | API facade, registry lookup, lock acquisition |
| `Conversation` | Message storage + seq + tombstone state |
| `ConversationRegistry` | CHM of conversations |
| `ConversationLockStriped` | Per-id mutex (Guava Striped or embedded lock) |
| `Message` | Immutable delivered record with seq |

### 3.2 ASCII diagram

```text
  Client                ChatStore                 Conversation
    │                      │                          │
    │ send(conv, draft)    │                          │
    ├─────────────────────►│ lock(conv)               │
    │                      ├─────────────────────────►│ deleted? → throw
    │                      │                          │ seq = nextSeq++
    │                      │                          │ messages[seq]=msg
    │                      │◄─────────────────────────┤
    │◄─────────────────────┤ SendResult(seq)          │
    │                      │ unlock                   │
    │                      │                          │
    │ deleteConversation   │                          │
    ├─────────────────────►│ lock(conv)               │
    │                      ├─────────────────────────►│ deleteSeq=maxSeq
    │                      │                          │ deleted=true
    │                      │ unlock                   │
    │                      │                          │
    │ listMessages         │                          │
    ├─────────────────────►│ lock(conv)               │
    │                      ├─────────────────────────►│ filter seq>deleteSeq
    │◄─────────────────────┤ List<Message>            │
```

### 3.3 Policy A vs Policy B (choose A for MVP)

| | Policy A (MVP) | Policy B (in-flight grace) |
|---|----------------|----------------------------|
| Send after delete | Always reject | May accept if "started" before delete |
| Complexity | Low | Needs epoch token / pre-delete lease |
| UX | Clean cut | Risk ghost messages |
| Interview | **Recommend A** | Mention as alternative |

This document implements **Policy A** throughout.

---

## 4. Core Data Structures & Algorithms

### 4.1 Sequence number assignment

```text
send under lock:
  seq = nextSeq++
  maxSeq = seq
  messages[seq] = new Message(seq, ...)
```

`nextSeq` starts at 1. Never reuse seq after delete (tombstone prevents new sends anyway).

### 4.2 Tombstone semantics

```text
deleteConversation under lock:
  if deleted: return                    // idempotent
  deleteSeq = maxSeq                   // hide all committed messages
  deleted = true
  deletedAt = Instant.now()
```

Messages remain in `messages` map physically (soft delete) but are **invisible** to readers.

**Phase 2 GC:** background job removes entries where `seq <= deleteSeq` after retention window.

### 4.3 Visibility function

```text
visible(msg, conv):
  return !conv.deleted || msg.seq > conv.deleteSeq

// Policy A equivalent since no post-delete sends:
// after delete, all stored msgs have seq <= deleteSeq → none visible
```

### 4.4 listMessages with cursor

```text
listMessages(conv, afterSeq, limit):
  start = max(afterSeq, conv.deleted ? conv.deleteSeq : 0)
  result = []
  for seq in conv.messages.tailMap(start, false).keySet():
    if result.size() == limit: break
    msg = conv.messages[seq]
    if visible(msg, conv):
      result.add(msg)
  return result
```

Using `TreeMap.tailMap` gives O(log N + k) for k results.

### 4.5 Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| send | O(log M) | TreeMap insert |
| delete | O(1) | Tombstone only |
| list | O(log M + k) | k = limit |
| getMeta | O(1) | Under lock |

M = messages in conversation.

---

## 5. Concurrency Invariants & Race Analysis

### 5.1 Locking strategy

```text
Lock L = lockStriped.get(conversationId)
L.lock()
try {
  // read/modify Conversation
} finally {
  L.unlock()
}
```

**Why per-conversation lock:** send/send on same chat must serialize seq assignment. delete/send must be ordered. Different chats scale horizontally.

**Do not** use one global lock — kills throughput.

**Do not** lock only on send but not delete — race window.

### 5.2 Linearization points

| Operation | Linearization point |
|-----------|---------------------|
| send | Message inserted in map with assigned seq (inside lock) |
| deleteConversation | `deleted=true` and `deleteSeq` written (inside lock) |
| listMessages | Snapshot taken under lock at iteration start |

### 5.3 Race timeline 1 — delete wins before send

```text
Time   Thread D (delete)                 Thread S (send)
──────────────────────────────────────────────────────────────────
t0     acquire lock(conv) ✓
t1     deleteSeq=5; deleted=true
t2     release lock
t3                                       acquire lock(conv)
t4                                       sees deleted → throw ConversationDeleted
t5                                       release lock
```

**Result:** No seq 6. Client gets error. Conversation empty on list.

### 5.4 Race timeline 2 — send wins before delete

```text
Time   Thread S (send)                   Thread D (delete)
──────────────────────────────────────────────────────────────────
t0     acquire lock ✓
t1     assign seq=6; store message
t2     release lock
t3                                       acquire lock
t4                                       deleteSeq=6; deleted=true
t5                                       release lock
```

**Result:** Message seq=6 existed briefly but `deleteSeq=6` → `visible` false (seq > deleteSeq is false). list returns empty. Send succeeded then conversation deleted — valid.

### 5.5 Race timeline 3 — concurrent sends

```text
Time   Thread S1                         Thread S2
──────────────────────────────────────────────────────────────────
t0     acquire lock ✓
t1     seq=5
t2     release lock
t3                                       acquire lock
t4                                       seq=6
t5                                       release lock
```

**Result:** Strict seq order 5 then 6. No duplicate seq — lock prevents.

### 5.6 Race timeline 4 — send waiting on lock while delete runs

```text
Time   Thread S                          Thread D
──────────────────────────────────────────────────────────────────
t0     blocked on lock
t1                                       acquire lock
t2                                       deleteSeq=4; deleted=true
t3                                       release lock
t4     acquire lock
t5     sees deleted → throw
```

**Policy A critical case:** Send **started** before delete (client initiated) but **commits** after delete → **rejected**. No ghost seq 5 visible later.

### 5.7 Race timeline 5 — list during delete

```text
Time   Thread R (list)                   Thread D (delete)
──────────────────────────────────────────────────────────────────
t0     acquire lock
t1     iterating msgs seq 1..3
t2                                       blocked on lock
t3     release lock (returned 1..3)
t4                                       acquire; deleteSeq=3; deleted=true
```

**Result:** R saw messages before delete — acceptable (may have read history). After delete, new lists empty. Optional: snapshot isolation not required MVP.

### 5.8 Buggy design — check-then-act outside lock

```text
// WRONG
if (!conv.deleted) {        // race window here
  lock()
  seq = nextSeq++
  ...
}
```

Two threads or delete interleaving → message after tombstone. **Always** check `deleted` **inside** lock.

### 5.9 Invariant table

| ID | Invariant |
|----|-----------|
| R1 | `nextSeq` incremented only under conv lock |
| R2 | `deleteSeq == maxSeq` at end of deleteConversation |
| R3 | If `deleted`, then `send` never succeeds |
| R4 | No two messages share same seq in one conv |
| R5 | `listMessages` filter consistent with visibility function |

---

## 6. Algorithms & Pseudocode

### 6.1 ChatStore.send

```text
send(conversationId, draft):
  validate draft.body non-empty
  conv = registry.getOrCreate(conversationId)
  lock = locks.lockFor(conversationId)
  lock.lock()
  try:
    if conv.deleted:
      throw ConversationDeletedException(conversationId, conv.deleteSeq)
    seq = conv.nextSeq++
    msg = Message(seq, draft.senderId, draft.body, now())
    conv.messages.put(seq, msg)
    conv.maxSeq = seq
    return SendResult(seq, true)
  finally:
    lock.unlock()
```

### 6.2 ChatStore.deleteConversation

```text
deleteConversation(conversationId):
  conv = registry.get(conversationId)
  if conv == null: throw NotFoundException
  lock = locks.lockFor(conversationId)
  lock.lock()
  try:
    if conv.deleted:
      return   // idempotent
    conv.deleteSeq = conv.maxSeq
    conv.deleted = true
    conv.deletedAt = now()
  finally:
    lock.unlock()
```

### 6.3 ChatStore.listMessages

```text
listMessages(conversationId, afterSeq, limit):
  validate limit > 0
  conv = registry.get(conversationId)
  if conv == null: throw NotFoundException
  lock = locks.lockFor(conversationId)
  lock.lock()
  try:
    cutoff = conv.deleted ? conv.deleteSeq : 0
    cursor = max(afterSeq, cutoff)
    out = []
    for seq in conv.messages.tailMap(cursor, false).keySet():
      if out.size() >= limit: break
      msg = conv.messages.get(seq)
      if msg.seq > cutoff:
        out.add(msg)
    return out
  finally:
    lock.unlock()
```

### 6.4 ChatStore.getMeta

```text
getMeta(conversationId):
  conv = registry.get(conversationId)
  if conv == null: throw NotFoundException
  lock.lock()
  try:
    return ConversationMeta(conv.deleted, conv.deleteSeq, conv.maxSeq, conv.deletedAt)
  finally:
    lock.unlock()
```

### 6.5 Auto-create vs explicit create

**MVP choice:** `send` calls `getOrCreate` — first message creates conversation. `deleteConversation` on unknown id throws NotFound.

### 6.6 WAL durability extension (Phase 2)

```text
append log record before applying mutation:
  SEND conv id seq payload
  DELETE conv id deleteSeq

replay:
  apply in order to rebuild in-memory state
  tombstone must replay before any later send on same conv
```

On recovery, reconstructed state must satisfy same invariants.

---

## 7. Failure Modes & Recovery

| Scenario | Failure | Mitigation |
|----------|---------|------------|
| Send without lock | Duplicate seq / ghost after delete | Per-conv lock mandatory |
| deleteSeq = nextSeq-1 wrong | Off-by-one visibility | Use maxSeq at commit |
| Clock-based visibility | Out-of-order with seq | Use seq only; deletedAt audit |
| Memory leak | Tombstoned msgs retained | GC job Phase 2 |
| Client retries send | Duplicate messages | Idempotency key Phase 2 |
| list during rapid delete | Stale read | Document acceptable |
| Striped lock hash collision | Unrelated convs block | Increase stripes |

### 7.1 Client-visible behavior summary

| State | send | list |
|-------|------|------|
| Active | OK, seq++ | msgs with seq > afterSeq |
| Deleted | ConversationDeleted | empty (all seq ≤ deleteSeq) |

---

## 8. Tests & Edge Cases

### 8.1 Functional tests

```java
@Test void sendThenRead() {
  var r = store.send("c1", draft("hi"));
  assertEquals(1, r.seq());
  var msgs = store.listMessages("c1", 0, 10);
  assertEquals(1, msgs.size());
}

@Test void deleteHidesMessages() {
  store.send("c1", draft("a"));
  store.send("c1", draft("b"));
  store.deleteConversation("c1");
  assertTrue(store.listMessages("c1", 0, 10).isEmpty());
}

@Test void sendAfterDeleteThrows() {
  store.deleteConversation("c1");
  assertThrows(ConversationDeletedException.class,
      () -> store.send("c1", draft("x")));
}

@Test void doubleDeleteIdempotent() {
  store.send("c1", draft("a"));
  store.deleteConversation("c1");
  store.deleteConversation("c1"); // no throw
  assertTrue(store.getMeta("c1").deleted());
}

@Test void seqMonotonic() {
  for (int i = 0; i < 5; i++) store.send("c1", draft("m"));
  assertEquals(5, store.getMeta("c1").maxSeq());
}
```

### 8.2 Race-specific tests

```java
@Test void deleteBeforeWaitingSend() throws Exception {
  CountDownLatch sendEntered = new CountDownLatch(1);
  CountDownLatch releaseDelete = new CountDownLatch(1);
  // Thread S blocks before lock; D deletes; S resumes → rejected
}

@Test void concurrentSendsUniqueSeq() throws Exception {
  int N = 100;
  ExecutorService ex = Executors.newFixedThreadPool(10);
  Set<Long> seqs = ConcurrentHashMap.newKeySet();
  for (int i = 0; i < N; i++)
    ex.submit(() -> seqs.add(store.send("c1", draft("x")).seq()));
  ex.shutdown();
  ex.awaitTermination(10, SECONDS);
  assertEquals(N, seqs.size()); // all unique
}
```

### 8.3 Scenario matrix (Policy A)

| Commit order | maxSeq at delete | deleteSeq | Post-delete list | Post-delete send |
|--------------|------------------|-----------|------------------|------------------|
| 3 sends then delete | 3 | 3 | empty | reject |
| delete then send | 0 | 0 | empty | reject |
| send seq=5, delete | 5 | 5 | empty | reject |
| delete empty conv | 0 | 0 | empty | reject |

### 8.4 Property invariant check

```java
@AfterEach void checkInvariants() {
  for (Conversation c : registry.all()) {
    assertTrue(c.deleteSeq <= c.maxSeq);
    if (c.deleted) {
      assertEquals(c.maxSeq, c.deleteSeq); // at commit instant
    }
  }
}
```

---

## 9. Complexity & Scalability Notes

### 9.1 Single-node limits

Per-conversation lock → hot chat with 10k msg/sec contends on one lock. Sharding by conversationId across processes fixes horizontal scale.

### 9.2 10× / 100× path

| Scale | Approach |
|-------|----------|
| 10× convs | Striped locks (8192 stripes) |
| 100× | Partition by conversationId hash to nodes |
| 1000× | Log-based storage (Kafka) + seq in event stream |

### 9.3 Databricks context

Notebook comment threads / job run discussions: delete thread must hide history for compliance UI. Seq-based tombstone is simpler than timestamp due to clock skew across executors — **server seq** is authoritative.

---

## 10. Wrap-Up

**Design summary**

- Monotonic per-conversation `seq` assigned under lock
- Tombstone: `deleted=true`, `deleteSeq=maxSeq`
- **Policy A:** reject send after delete
- `listMessages` filters `seq > deleteSeq`
- Race timelines prove linearizability

**MVP vs Phase 2**

| MVP | Phase 2 |
|-----|---------|
| In-memory | WAL + replay |
| Policy A | Policy B in-flight tokens |
| Global delete | Per-message delete |

**Top mistakes**

1. Check deleted outside lock
2. Using wall clock instead of seq for visibility
3. Global lock on all conversations
4. Allowing send after tombstone (ghost messages)

---
""",
        qa_block([
            (
                "Why tombstone instead of deleting messages immediately?",
                "O(1) delete vs O(M) message removal. Tombstone preserves audit trail "
                "and simplifies concurrent readers — list filters by deleteSeq. "
                "Background GC can compact later.",
            ),
            (
                "Why Policy A (reject send after delete)?",
                "Simplest correct semantics: once user deletes conversation, no new "
                "messages appear. Avoids ghost messages and epoch/token complexity. "
                "Policy B only if product requires in-flight send grace period.",
            ),
            (
                "What is deleteSeq?",
                "At delete commit, capture `maxSeq` — the highest seq assigned to any "
                "committed message. All messages with seq ≤ deleteSeq become invisible. "
                "Under Policy A, no seq > deleteSeq will ever be created.",
            ),
            (
                "Send starts before delete, commits after — what happens?",
                "Under Policy A with per-conv lock: if delete acquires lock first, send "
                "sees tombstone and throws. If send acquires lock first, message gets seq "
                "then delete sets deleteSeq=maxSeq hiding it. Send never succeeds after "
                "tombstone is visible to lock holder.",
            ),
            (
                "Why not use deletedAt timestamp for visibility?",
                "Clock skew and concurrent assignments make wall time unreliable. "
                "Monotonic seq assigned under same lock as delete gives total order.",
            ),
            (
                "Do you need vector clocks?",
                "Not for single-server per-conversation seq. Vector clocks help "
                "multi-region without central seq issuer — out of MVP scope.",
            ),
            (
                "How is per-conversation lock implemented?",
                "Guava Striped<Lock> with 8192 stripes, or embed `ReentrantLock` in "
                "Conversation object created on first access. Key: same lock for "
                "send/delete/list on one convId.",
            ),
            (
                "Is double delete safe?",
                "Yes — idempotent. Second call sees deleted=true and returns without "
                "changing deleteSeq or deletedAt.",
            ),
            (
                "What does client show after delete?",
                "listMessages returns empty. getMeta shows deleted=true, deleteSeq. "
                "Client clears local cache for seq ≤ deleteSeq.",
            ),
            (
                "How test the delete-vs-send race?",
                "Use CountDownLatch: pause send thread before lock, run delete, release "
                "send → assert ConversationDeletedException. Reverse order test for "
                "send-then-delete hiding message.",
            ),
        ]),
        """
## 12. Appendices

### A. Scenario timeline diagram (ASCII)

```text
        SEND (success)          DELETE              SEND (reject)
              │                    │                      │
seq:  ──1──2──3──4──5──────────────X tombstone          ✗
              │              deleteSeq=5                 │
visible:  all 1-5           none (seq>5 false)        N/A
```

### B. Whiteboard timing (45 min)

| Phase | Min | Content |
|-------|-----|---------|
| Clarify | 5 | Delete scope, Policy A, seq |
| API | 7 | send/delete/list/meta |
| Data model | 8 | TreeMap, tombstone fields |
| Pseudocode | 10 | Three ops under lock |
| Races | 10 | Timelines 1-4 |
| Tests + Q&A | 5 | One latch test |

### C. Glossary

| Term | Meaning |
|------|---------|
| Tombstone | Metadata mark that conversation is deleted without immediate purge |
| deleteSeq | Seq threshold: messages with seq ≤ deleteSeq hidden |
| Policy A | Reject all sends after delete commits |
| maxSeq | Highest seq assigned to any stored message |
| Linearizability | Ops appear to execute atomically in some serial order |

### D. Final checklist

- [ ] Policy A stated explicitly
- [ ] deleteSeq = maxSeq at commit
- [ ] deleted check inside lock on send
- [ ] Per-conversation lock (not global)
- [ ] list filters seq > deleteSeq
- [ ] Race timelines drawn on board
- [ ] Idempotent delete tested
""",
        footer(),
    ]
    return "\n".join(parts)


def main() -> None:
    files = [
        ("cidr-firewall-matcher-lld-system-design.md", cidr_doc()),
        ("chat-deletion-concurrent-sends-lld-system-design.md", chat_doc()),
    ]
    for name, content in files:
        path = OUT / name
        path.write_text(content, encoding="utf-8")
        lines = len(content.splitlines())
        print(f"{name}: {lines} lines")
        if not (650 <= lines <= 850):
            print(f"  WARNING: outside 650-850 range")


if __name__ == "__main__":
    main()
