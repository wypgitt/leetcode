#!/usr/bin/env python3
"""Generate thorough Apple Bank C system-design markdown files (700–1000 lines)."""
from __future__ import annotations

from pathlib import Path

from _bank_c_helpers import APPLE_LENS, base_apps, base_qa
from _bank_c_specs import MORE_SPECS

OUT = Path(__file__).resolve().parent
SKIP = {"icloud-photo-library-sync-system-design.md"}


def expand(spec: dict) -> str:
    t = spec
    title = t["title"]
    end = t.get("end_name", title.lower())
    apple_lens = t.get("apple_lens", APPLE_LENS)

    fr = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in t["fr"])
    nfr = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in t["nfr"])
    mvp = "\n".join(f"{i}. {x}" for i, x in enumerate(t["mvp"], 1))
    outmvp = "\n".join(f"- {x}" for x in t["outmvp"])
    happy = "\n".join(f"{i}. {x}" for i, x in enumerate(t["happy"], 1))
    edges = "\n".join(f"| {a} | {b} |" for a, b in t["edges"])
    scales = "\n".join(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in t["scales"])
    jumps = "\n".join(f"- **{k}:** {v}" for k, v in t["jumps"])
    cons = "\n".join(f"- {x}" for x in t["constraints"])
    opts = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in t["options"])
    trade = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in t["tradeoffs"])
    risks = "\n".join(f"- {x}" for x in t["risks"])

    est = []
    for i, (h, body) in enumerate(t["estimation"], 1):
        est.append(f"### 2.{i} {h}\n\n{body}\n")
    est_s = "\n".join(est)

    dd = []
    for i, (h, body) in enumerate(t["deep"], 1):
        dd.append(f"### 5.{i} {h}\n\n{body}\n")
    dd_s = "\n".join(dd)

    qa_sections = base_qa(title, t.get("qa_extra", []))
    qa = ["## 7. Deeper / Related Interview Questions\n"]
    for i, (h, pairs) in enumerate(qa_sections, 1):
        qa.append(f"\n### 7.{i} {h}\n")
        for q, a in pairs:
            qa.append(f"\n**Q: {q}**  \nA: {a}\n")
    qa_s = "".join(qa)

    app_sections = base_apps(title, t.get("apps_extra", []))
    ap = ["## 8. Appendices\n"]
    for i, (h, body) in enumerate(app_sections, 1):
        ap.append(f"\n### 8.{i} {h}\n\n{body}\n")

    ap.append(f"""
### 8.{len(app_sections) + 1} Client sync agent pseudocode

```text
loop:
  wait(push_dirty OR timer OR user_action OR battery_ok_window)
  if not network_allowed(): continue
  push_outbox_batch(limit=K)
  pull_since(cursor, limit=K)
  apply_idempotent(mutations)
  ack_cursor()
  maybe_compact_local()
```

### 8.{len(app_sections) + 2} Home-cell failover note

```text
epoch++
fence old primary writes
clients retry with backoff
in-flight ops idempotent by mutation_id
expect at-least-once delivery of sync ops
```

### 8.{len(app_sections) + 3} What "done" looks like in 45 minutes

- Clear MVP scope  
- Correct trust boundary (on-device vs server)  
- One coherent diagram  
- Conflict resolution example  
- Scale + battery paragraph  
- Honest non-goals  

### 8.{len(app_sections) + 4} Cellular / Wi‑Fi policy matrix

| Condition | Metadata sync | Small payloads | Large blobs |
|-----------|---------------|----------------|-------------|
| Wi‑Fi | Yes | Yes | Yes |
| Cellular default | Yes | Recent/small | Defer |
| Cellular + user allow | Yes | Yes | Budget-capped |
| Low Power Mode | Coalesce | Defer | Defer |
| Charging + Wi‑Fi | Max throughput | Max | Max |

### 8.{len(app_sections) + 5} Interview traps (expanded)

| Trap | Pushback |
|------|----------|
| Server reads user content under E2E claim | Contradiction—call ADP/E2E fork |
| Evict local before cloud ACK | Data-loss bug |
| Poll every few seconds | Battery death |
| Dual active writers without merge | Split brain |
| Unit errors (PB vs TB) | Show arithmetic always |
| "We'll add privacy later" | Apple bar: privacy-first architecture |

---

*End of {end} system design.*
""")

    extras = t.get("extras", "")

    return f"""# System Design: {title}

> **Focus areas:** {t["focus"]}  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths, Apple-style privacy / on-device boundaries

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

Goal: {t["goal"]}
{apple_lens}
### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
{fr}

**MVP functional scope (lock with interviewer):**

{mvp}

**Out of MVP (explicitly defer):**

{outmvp}

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
{nfr}

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

{happy}

**Edge / failure cases**

| Case | Behavior |
|------|----------|
{edges}

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
{scales}

**What each jump forces:**

{jumps}

### 1.5 Etc. (Constraints & Assumptions)

{cons}

**Scope statement:**

> {t["scope"]}

---

## 2. Back-of-the-Envelope Estimation

{est_s}
### 2.{len(t["estimation"]) + 1} Unit-check traps

{t["unit_traps"]}

### 2.{len(t["estimation"]) + 2} Critical bottlenecks (rank ordered)

{t["bottlenecks"]}

---

## 3. High-Level Design

### 3.1 Core abstractions

{t["abstractions"]}

### 3.2 On-device vs server split

{t["split"]}

### 3.3 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
{opts}

**Chosen path:** {t["chosen"]}

### 3.4 Privacy, trust, and encryption

{t["privacy"]}

### 3.5 Consistency, sync, and conflict resolution

{t["consistency"]}

### 3.6 Offline-first behavior

{t["offline"]}

### 3.7 Battery, radio, and scheduling

{t["battery"]}

### 3.8 Multi-region / cell model

{t["region"]}

### 3.9 Abuse, auth, and quotas

{t["abuse"]}

### 3.10 Key invariants (state these explicitly)

1. **Local durability before UI ACK** for user-initiated writes.
2. **Cloud durability before local eviction** of the last copy of user data (where applicable).
3. **Idempotent apply** — replay of the same `op_id` / `mutation_id` / `message_id` is safe.
4. **Tombstones for delete** — never silently drop data without retention policy.
5. **Single-writer home cell** per user/library/device shard to avoid split brain.
6. **Battery-aware radio use** — coalesce wakes; defer large payloads on cellular/LPM unless user-visible.

{extras}

### 3.11 Advanced Data Protection (ADP) fork

| Mode | Server sees | On-device responsibility |
|------|-------------|---------------------------|
| ADP / E2E on | Ciphertext blobs + opaque sync envelopes | Decrypt, merge, ML, search |
| Standard protection | May allow richer server-side features | Still minimize retention; disclose trade-off |

**Interview win:** Offer both modes; do not claim server plaintext AI/derivatives while ADP E2E holds.

---

## 4. Architecture Diagram

{t["diagram"]}

---

## 5. Design Deep Dive

{dd_s}
---

## 6. Wrap-Up

### 6.1 What we designed

{t["designed"]}

### 6.2 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
{trade}

### 6.3 MVP → scale path

{t["path"]}

### 6.4 Risks

{risks}

---

{qa_s}
---

{"".join(ap)}
"""


def imessage_spec() -> dict:
    from _bank_c_helpers import S, std_estimation

    return S(
        title="iMessage Multi-Device Delivery",
        filename="imessage-multidevice-delivery-system-design.md",
        focus="E2E encryption · Per-device fan-out · Offline mailboxes · Push coalescing · Attachments · Battery · Key directory",
        goal="**bound delivery**—how a message reaches all of a user's devices with E2E encryption, without the server reading content.",
        scope="Design an E2E multi-device iMessage-style delivery system: per-device encryption, durable offline mailboxes, attachment ciphertext, group fan-out, push wakes, and progressive scale—without the server reading message bodies.",
        end_name="iMessage multi-device delivery",
        entity="recipient_device_id",
        sync_primitive="Per-device mailbox queue",
        fr=[
            ("F1", "Who sends/receives?", "Apple ID users with registered devices; SMS fallback out of band", "Separate iMessage path vs PSTN"),
            ("F2", "Delivery semantics?", "At-least-once to each device; UI dedupe", "Per-device queues + ack"),
            ("F3", "E2E?", "Yes—server cannot read bodies", "Encrypt per recipient device"),
            ("F4", "Multi-device?", "All signed-in devices receive", "Fan-out envelopes + self devices"),
            ("F5", "Offline?", "Queue until online; TTL days", "Durable mailbox"),
            ("F6", "Attachments?", "Encrypted blob refs", "Pointer + file key inside E2E body"),
            ("F7", "Groups?", "N members × M devices", "Fan-out; later sender-keys"),
            ("F8", "Receipts?", "Delivered/read optional", "Encrypt receipts; user toggles"),
            ("F9", "Edit/unsend?", "Windowed edit; best-effort unsend", "Mutation messages + tombstones"),
            ("F10", "Spam?", "Prefer on-device", "Anonymous server signals only"),
            ("F11", "Registration?", "Trusted device enrollment", "Key directory updates"),
            ("F12", "Push?", "APNs wakes; minimal payload", "Push as signal, not content"),
        ],
        mvp=["Register device keys", "Send 1:1 with per-device envelopes", "Per-device mailbox + ack GC", "Self-fanout to sender devices", "Encrypted attachments", "Basic group fan-out", "Coalesced push wakes"],
        outmvp=["Full MLS lecture", "SMS/RCS gateway internals", "Business chat server search", "Guaranteed unsend against offline adversary"],
        nfr=[
            ("N1", "Confidentiality", "E2E", "Server sees envelopes only"),
            ("N2", "Latency", "Interactive", "p50 < 300ms online"),
            ("N3", "Offline durability", "Days", "Multi-AZ mailbox"),
            ("N4", "Battery", "Push not poll", "Coalesce APNs"),
            ("N5", "Integrity", "Tamper-evident", "AEAD"),
            ("N6", "Availability", "99.99% send", "Retry + degrade"),
            ("N7", "Fan-out cost", "Groups OK", "Optimize later"),
            ("N8", "Metadata privacy", "Minimize", "Pad sizes; short logs"),
        ],
        happy=["A sends to B; all B devices decrypt; receipts return", "B offline; queue; fetch; ack; GC", "A's Mac+iPhone show sent via self-fanout", "Attachment upload ciphertext + pointer", "New iPad receives subsequent messages"],
        edges=[("Stolen device", "Revoke keys; no new decrypt"), ("Key directory poison", "Transparency/attest; warn on key change"), ("Duplicate delivery", "Dedupe message_id"), ("Partial group fail", "Retry missing devices"), ("APNs loss", "Pull reconcile"), ("Huge group", "Sender-keys; rate limits"), ("Attachment orphan", "Refcount + TTL GC"), ("Decrypt fail", "Quarantine + session repair")],
        scales=[("Active users", "50M", "500M", "500M+", "500M+"), ("Messages/day", "10B", "100B", "1T", "10T"), ("Peak send QPS", "200K", "2M", "20M", "200M"), ("Devices/user", "3", "3", "3.5", "4"), ("Avg envelope", "1KB", "1KB", "1.2KB", "1.5KB"), ("Mailbox depth p99", "500", "500", "1K", "2K"), ("Attachment uploads/day", "500M", "5B", "50B", "500B"), ("Group size p99", "50", "50", "100", "200")],
        jumps=[("10×", "Shard mailboxes; key cache; APNs coalesce"), ("100×", "Regional gateways; attachment edge; fanout workers"), ("1,000×", "Sender-keys/MLS; sealed sender; metadata minimization")],
        constraints=["Server untrusted for content", "Metadata still sensitive", "SMS is different channel", "Not designing full APNs internals"],
        estimation=std_estimation("iMessage envelopes", "10B/day × 1 KB ≈ 10 TB/day", "1–1.5 KB", "2×"),
        unit_traps="""| Claim | Truth |
|-------|-------|
| 10B×1KB=10PB/day | **10 TB/day** |
| Fan-out is free | Multiply by devices |
| Peak = average | Use 2–5× |""",
        bottlenecks="""1. Per-device mailbox write QPS  
2. Key directory under send storms  
3. Attachment object store  
4. Sender encrypt CPU for large groups  
5. APNs storms  
6. Ack/GC races""",
        abstractions="""```text
User, Device(identity_key, push_token)
Conversation, Message(message_id)
Envelope(recipient_device_id, ciphertext)
MailboxQueue(device_id)
AttachmentBlob(blob_ref)
KeyDirectory(user → device key bundles)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Encrypt/decrypt | Yes | No |
| Key gen | Secure Enclave | Public keys only |
| Mailbox | Local outbox | Durable per-device queue |
| Spam ML | Prefer on-device | Anonymous signals |
| Push payload | — | Opaque wake |""",
        options=[("A. Server plaintext fan-out", "Easy", "Breaks E2E", "Privacy required"), ("B. One user key all devices", "Fewer encrypts", "Revoke weak", "Device revoke needed"), ("C. Per-device envelopes (+ sender-keys later)", "Proper revoke", "Costly fan-out", "— chosen"), ("D. Pure P2P", "Max privacy", "Offline hard", "Mobile offline")],
        chosen="Per-device ciphertext envelopes into durable mailboxes; APNs as wake; evolve large groups to sender-keys.",
        privacy="Sender fetches recipient device pubkeys; AEAD per device (ratchet). Server routes opaque envelopes. Attachments: `file_key` lives inside E2E body; blob store holds ciphertext only.",
        consistency="Eventual delivery; per-device `arrival_seq`; client dedupe by `message_id`; edits/unsends are new messages referencing targets.",
        offline="Durable outbox before UI sent; recipient mailbox until fetch+ack; history via encrypted backup (related system).",
        battery="Coalesce APNs per conversation; backup pull while active; defer large attachments on cellular.",
        region="Home cell for mailbox metadata; global send anycast → forward; regional attachment placement.",
        abuse="Rate limits; registration friction; on-device spam; report bundles without plaintext retention.",
        diagram="""```text
iPhone A / Mac A → Send API → Key Directory
                 → Fanout Service → Mailboxes (B1,B2,B3)
                 → APNs wake → devices pull/ack
                 → Attachment Object Store (ciphertext)
```

**Send path:** UI → outbox → fetch keys → encrypt N envelopes → persist mailboxes → wake → pull → decrypt → ACK.""",
        designed="E2E multi-device messaging: clients encrypt per device, servers fan out opaque envelopes to durable mailboxes, APNs wakes devices, attachments are ciphertext, groups evolve to sender-keys.",
        tradeoffs=[("E2E vs server search", "E2E", "Privacy"), ("Per-device vs per-user key", "Per-device", "Revocation"), ("Push content vs signal", "Signal", "Privacy/size"), ("Global order", "Per-device mailbox order", "Scale")],
        path="MVP: 1:1+simple groups, mailboxes, attachments. 10–100×: shards + fanout fleet. 1000×: sender-keys, sealed sender.",
        risks=["Key directory poison", "Metadata leakage", "Fan-out cost", "Ack/GC races"],
        qa_extra=[("Messaging-specific", [("Exactly-once to UI?", "At-least-once + client dedupe."), ("Why encrypt to my own Mac?", "Multi-device thread visibility with per-device keys."), ("Can Apple read messages?", "Not bodies under E2E; metadata still sensitive.")])],
        apps_extra=[("Envelope schema", """```text
Envelope {{ message_id, conversation_id, recipient_device_id, ciphertext, ratchet_header, arrival_seq }}
```"""), ("API checklist", """- [ ] Register/Revoke device  
- [ ] GetKeyBundle  
- [ ] SendEnvelopes  
- [ ] FetchMailbox / Ack  
- [ ] Attachment sessions""")],
        deep=[
            ("Reliability & delivery invariants", """1. Persist all envelopes before send ACK.  
2. ACK deletes only after local durable store.  
3. Dedupe `message_id`.  
4. Revoked devices receive no new envelopes.

| Failure | Mitigation |
|---------|------------|
| Sender crash post-accept | Server receipt; outbox reconciles |
| Mailbox AZ loss | Quorum write |
| Decrypt fail | Session repair UI |
| Push loss | Pull reconcile |"""),
            ("Scalability", "Shard mailbox by `recipient_device_id`; fanout workers; key caches. Groups: MVP per-device → sender-keys → MLS-style at extreme."),
            ("Maintainability", "Envelope versioning; ratchet agility; feature flags for edit/unsend; don't brick old devices."),
            ("Crypto sketch (interview-depth)", """```text
X3DH-like session from prekeys → Double Ratchet 1:1
Multi-device: session per device
Groups: fan-out sealed boxes → sender chain keys
```
Naming Signal-style primitives is enough; don't implement crypto in 45 minutes."""),
            ("Attachments", "Encrypt file with `file_key` → chunk upload → message carries `blob_ref + file_key` inside E2E body → recipients download ciphertext."),
            ("Registration & trust", "Auth + optional existing-device approval; publish keys; history transfer via QR/proximity/encrypted backup—separate design."),
        ],
        extras="""
### 3.12 Group messaging evolution path

| Phase | Approach | When |
|-------|----------|------|
| MVP | Per-device envelope fan-out | Small groups, 1:1 |
| 10× | Sender chain keys | Medium groups |
| 1000× | MLS-style group sessions | Large groups, lower encrypt CPU |

**Sealed sender (phase 2):** Hide sender identity from server metadata where product allows—separate key server trust assumptions.
""",
    )


def write_all() -> list[tuple[str, int]]:
    specs = [imessage_spec()] + MORE_SPECS
    results = []
    for spec in specs:
        fname = spec["filename"]
        if fname in SKIP:
            continue
        text = expand(spec)
        (OUT / fname).write_text(text)
        n = len(text.splitlines())
        results.append((fname, n))
        status = "OK" if 700 <= n <= 1000 else "WARN"
        print(f"{fname}: {n} [{status}]")
    return results


if __name__ == "__main__":
    write_all()
