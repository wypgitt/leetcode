# LLD: Chat Conversation Delete vs Concurrent Sends

> **Focus areas:** Tombstone deleteSeq · Monotonic seq · Policy A reject-after-delete · Per-conversation lock · Race timelines
> **Style:** LLD interview (clarify → API → classes → concurrency invariants → pseudocode → failure/recovery → tests → Q&A)
> **Quality bar:** Strict visibility: no message with seq ≤ deleteSeq after delete; send after delete rejected; races linearized per conversation
> **Interview theme:** Databricks — signature storage/concurrency LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Core Data Structures & Algorithms](#4-core-data-structures--algorithms)
5. [Concurrency Invariants & Race Analysis](#5-concurrency-invariants--race-analysis)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Tests & Edge Cases](#8-tests--edge-cases)
9. [Complexity & Scalability Notes](#9-complexity--scalability-notes)
10. [Wrap-Up](#10-wrap-up)
11. [Interviewer Q&A (with Answers)](#11-interviewer-qa-with-answers)
12. [Appendices](#12-appendices)

---

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

## 11. Interviewer Q&A (with Answers)

### Q1. Why tombstone instead of deleting messages immediately?

O(1) delete vs O(M) message removal. Tombstone preserves audit trail and simplifies concurrent readers — list filters by deleteSeq. Background GC can compact later.

### Q2. Why Policy A (reject send after delete)?

Simplest correct semantics: once user deletes conversation, no new messages appear. Avoids ghost messages and epoch/token complexity. Policy B only if product requires in-flight send grace period.

### Q3. What is deleteSeq?

At delete commit, capture `maxSeq` — the highest seq assigned to any committed message. All messages with seq ≤ deleteSeq become invisible. Under Policy A, no seq > deleteSeq will ever be created.

### Q4. Send starts before delete, commits after — what happens?

Under Policy A with per-conv lock: if delete acquires lock first, send sees tombstone and throws. If send acquires lock first, message gets seq then delete sets deleteSeq=maxSeq hiding it. Send never succeeds after tombstone is visible to lock holder.

### Q5. Why not use deletedAt timestamp for visibility?

Clock skew and concurrent assignments make wall time unreliable. Monotonic seq assigned under same lock as delete gives total order.

### Q6. Do you need vector clocks?

Not for single-server per-conversation seq. Vector clocks help multi-region without central seq issuer — out of MVP scope.

### Q7. How is per-conversation lock implemented?

Guava Striped<Lock> with 8192 stripes, or embed `ReentrantLock` in Conversation object created on first access. Key: same lock for send/delete/list on one convId.

### Q8. Is double delete safe?

Yes — idempotent. Second call sees deleted=true and returns without changing deleteSeq or deletedAt.

### Q9. What does client show after delete?

listMessages returns empty. getMeta shows deleted=true, deleteSeq. Client clears local cache for seq ≤ deleteSeq.

### Q10. How test the delete-vs-send race?

Use CountDownLatch: pause send thread before lock, run delete, release send → assert ConversationDeletedException. Reverse order test for send-then-delete hiding message.


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


---

*End of LLD prep.*
