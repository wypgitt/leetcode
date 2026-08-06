"""Chat deletion concurrent sends LLD topic."""

from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices

register("chat-deletion-concurrent-sends-lld-system-design.md", lambda: build_doc([
    header(
        "Chat Conversation Delete vs Concurrent Sends",
        "Tombstones · Sequence numbers · deleted_at · Visibility rules · Ordering send/delete",
        "No message visible after delete if seq ≤ delete_seq; in-flight sends ordered deterministically",
    ),
    section_1(
        goal="Design **chat message storage** where **global delete conversation** races with **in-flight sends**, using tombstones, sequence numbers, and visibility rules (`deleted_at` vs message `seq`).",
        what_is="""| Scope | Single conversation store | Full messaging product |
| Ops | send, deleteConversation, read | Edit/react Phase 2 |
| Ordering | Per-conversation monotonic seq | Global total order |
| Databricks lens | Metadata lifecycle / soft delete | Multi-region chat |""",
        fr_rows=[
            ("Delete scope?", "Whole conversation tombstone", "Not single message MVP"),
            ("Sequence?", "Monotonic seq per conversation on send", "Compare to delete_seq"),
            ("Visibility?", "Message visible iff seq > delete_seq at read time", "Define strict rule"),
            ("Concurrent send/delete?", "Both may be in flight", "Linearize per conversation"),
            ("delete marker?", "deleted_at timestamp + delete_seq", "Tombstone record"),
            ("Send after delete?", "Rejected or ghost invisible", "Pick: reject send if deleted"),
            ("Read API?", "listMessages after cursor", "Filter invisible"),
            ("Durability?", "In-memory MVP or WAL", "Persist tombstone"),
            ("User experience?", "Delete wins for msgs at or before delete point", "Late sends dropped"),
            ("Idempotent delete?", "Second delete no-op", "Yes"),
            ("Multi-thread?", "Concurrent sends + one delete", "Lock per conversation"),
            ("Ordering guarantee?", "Seq reflects commit order", "Not wall clock only"),
        ],
        mvp=[
            "Conversation state: messages map seq→Message, tombstone optional.",
            "send: assign seq if not deleted; else reject ConversationDeleted.",
            "deleteConversation: set delete_seq = current max seq (or next-1 policy); tombstone.",
            "read: return messages where seq > delete_seq (or sent before delete committed — define).",
            "Linearize: conversation lock for send vs delete.",
            "Document race: send started before delete but commits after → policy.",
        ],
        scope="Chat store with global delete vs concurrent sends: tombstones, monotonic seq, visibility by delete_seq, deterministic ordering rules.",
        invariant="""After deleteConversation completes at delete_seq = D:
  no client observes messages with seq ≤ D unless they were read before delete (snapshot isolation optional).
send that acquires seq S after delete committed with D: rejected if S would be ≤ D or always rejected once tombstone set (pick one policy and document).
Sequence numbers strictly increase for accepted sends.""",
    ),
    section_2(
        api="""class ChatStore:
  SendResult send(conversationId, Message msg)
  void deleteConversation(conversationId)
  List<Message> listMessages(conversationId, afterSeq, limit)
  ConversationMeta getMeta(conversationId)

class ConversationMeta:
  boolean deleted
  long deleteSeq
  long maxSeq
  Instant deletedAt

class SendResult:
  long seq
  boolean accepted""",
        guarantees=[
            ("Seq monotonic", "Accepted sends get increasing seq"),
            ("Delete linearizable", "deleteConversation atomic per conversation"),
            ("Visibility", "Post-delete reads exclude seq ≤ deleteSeq per policy"),
            ("No resurrect", "Deleted conversation stays deleted MVP"),
            ("Concurrent safety", "No lost messages or seq collision"),
        ],
        errors="""ConversationDeleted — send after delete
NotFound — unknown conversationId
InvalidArgument — empty body
ClosedException — shutdown""",
    ),
    section_3(
        classes=[
            ("ChatStore", "API facade"),
            ("Conversation", "messages, tombstone, nextSeq"),
            ("Message", "seq, body, sender, createdAt"),
            ("Tombstone", "deleteSeq, deletedAt"),
            ("ConversationLock", "Per-id mutex"),
            ("SeqGenerator", "nextSeq++ under lock"),
        ],
        diagram="""send ──lock(conv)──> if deleted: reject
                  else assign seq, store
delete ──lock(conv)──> deleteSeq = maxSeq; tombstone=true
read ──lock(conv)──> filter seq > deleteSeq""",
    ),
    section_4("""### 4.1 Visibility policies (pick one)

**Policy A — Delete seq at commit time:**
```text
delete: deleteSeq = maxSeq
visible(msg): msg.seq > deleteSeq
send after delete: always rejected
```

**Policy B — In-flight grace:**
```text
send started before delete token acquired: may commit with seq S
delete sets deleteSeq = maxSeq at delete time
visible: msg.seq > deleteSeq OR msg had pre-delete token
MVP: prefer Policy A for simplicity
```

### 4.2 Ordering table

| Event order | Result |
|-------------|--------|
| send then delete | msg visible until delete; then hidden on read |
| delete then send | send rejected |
| concurrent | lock orders; later op sees tombstone or higher seq |

| Op | Time | Notes |
|----|------|-------|
| send | O(1) | Under conv lock |
| delete | O(1) | Tombstone |
| list | O(k) | k limit |"""),
    section_5(
        "| Conversation | dedicated lock per id |\n| ChatStore map | CHM convId → Conversation |",
        ["Seq assigned only under lock.", "deleteSeq ≤ maxSeq always.", "Tombstone sticky.", "No seq reuse.", "listMessages filters consistently.", "delete idempotent."],
        "lock(conversationId) for send/delete/read modifying view",
    ),
    section_6([
        ("send", """lock(conv):
  if conv.deleted: throw ConversationDeleted
  seq = conv.nextSeq++
  msg.seq = seq
  conv.messages.put(seq, msg)
  conv.maxSeq = seq
unlock
return SendResult(seq)"""),
        ("deleteConversation", """lock(conv):
  if conv.deleted: return
  conv.deleteSeq = conv.maxSeq
  conv.deleted = true
  conv.deletedAt = now()
unlock"""),
        ("listMessages", """lock(conv):
  out = []
  for seq in sorted(conv.messages.keys()):
    if seq > conv.deleteSeq:
      out.add(conv.messages[seq])
unlock
return out"""),
        ("race narrative", """Thread S: send begins, waits for lock
Thread D: delete sets deleteSeq=5, deleted=true
Thread S: acquires lock, sees deleted, reject send
// no seq 6 after delete"""),
        ("alt in-flight token", """send:
  if conv.deleted: reject
  token = conv.epoch
  ... build msg ...
  lock:
    if conv.epoch != token or conv.deleted: reject
    assign seq"""),
    ]),
    section_7([
        ("Send after delete", "Rejected", "ConversationDeleted"),
        ("Delete during list", "Snapshot under lock", "Consistent filter"),
        ("Lost message without lock", "Duplicate seq", "Per-conv lock prevents"),
        ("Clock vs seq", "Use seq not wall clock", "deletedAt audit only"),
        ("Partial read cursor", "afterSeq skips deleted", "Document cursor semantics"),
    ]),
    section_8(
        ["send read back", "delete hides prior msgs", "send after delete fails", "double delete idempotent", "seq monotonic", "list empty after delete all"],
        ["concurrent sends unique seq", "delete vs send race deterministic", "many conversations parallel"],
        None,
    ),
    section_9("Shard by conversationId; async delete propagation; retention GC of tombstoned messages; CRDT merge out of scope."),
    section_10(
        ["Tombstone + deleteSeq", "Per-conversation lock", "Reject post-delete sends (Policy A)", "Filter on read"],
        [("In-memory", "WAL + replication"), ("Global delete", "Per-message delete")],
        ["Seq assigned after delete check missing", "Visible msgs after delete", "No lock on send/delete"],
    ),
    section_11(
        ["WhatsApp delete for everyone?", "Soft delete retention?", "Client optimistic UI?", "Vector clocks needed?", "GDPR hard delete?"],
        [("Wall clock ordering", "Use seq"), ("Show deleted msgs", "Filter by deleteSeq")],
    ),
    section_12(common_appendices("chat-deletion-concurrent-sends")),
]))
