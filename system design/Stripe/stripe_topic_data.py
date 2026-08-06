"""Topic-specific content for Stripe system design doc generation."""

from __future__ import annotations

TOPICS = [{'file': 'transaction-apis-log-system-design.md',
  'title': 'Transaction APIs + Transaction Log',
  'focus': 'Public transaction APIs · Append-only log · Idempotency keys · Strong consistency · '
           'Audit trail · Regional routing · API versioning',
  'scope': 'Design public-facing transaction APIs backed by an immutable transaction log: '
           'idempotent writes, typed errors, pagination, audit forever, and single-writer home '
           'cells—from ~500 write QPS through 10× / 100× / 1,000× with correct retry semantics and '
           'ledger integration.',
  'goal': 'bound the **transaction API + immutable log** layer—what gets logged, who may write, '
          'how reads relate to the log, and how idempotency ties API semantics to durable history.',
  'functional_reqs': [('Who writes?',
                       'Merchant integrations + internal services via API keys',
                       'AuthN/Z; scoped write permissions per resource type'),
                      ('What is logged?',
                       'Every state transition as append-only log entry',
                       'Log is SoT for audit; resource row is materialized view'),
                      ('Idempotency?',
                       'Mandatory on POST/PATCH that mutate money-adjacent state',
                       '`Idempotency-Key` + body hash; long retention'),
                      ('Read models?',
                       'GET by id, list with filters, cursor pagination',
                       'Stable sort key; snapshot vs live documented'),
                      ('Versioning?',
                       'Explicit API version header / URL prefix',
                       'Expand/contract migrations; deprecation window'),
                      ('Consistency?',
                       'RYW for resource after write',
                       'Route reads to home cell or version token'),
                      ('Partial updates?',
                       'PATCH with optimistic concurrency (version/etag)',
                       'Reject stale writes with 409'),
                      ('Cancel/reverse?',
                       'Terminal transitions via dedicated endpoints',
                       'Append CANCELLED log entry; never delete'),
                      ('Multi-tenant?',
                       'Strict merchant isolation',
                       '`merchant_id` on all rows; ACL on every query'),
                      ('Export/audit?',
                       'Immutable history forever',
                       'Hot OLTP + cold archive; legal hold'),
                      ('Webhooks?',
                       'Emit on log append via outbox',
                       'Stable `event_id`; at-least-once delivery'),
                      ('Ledger tie-in?',
                       'Economic transitions post journal after log commit',
                       '`journal_key` derived from `transaction_id:transition`')],
  'mvp': ['`POST /v1/transactions` — create with idempotency.',
          '`GET /v1/transactions/{id}` — fetch current state + latest log seq.',
          '`GET /v1/transactions` — cursor list by merchant, status, time.',
          '`POST /v1/transactions/{id}/cancel` — idempotent terminal transition.',
          'Append-only transaction log with typed transitions.',
          'Audit envelope on every mutation.'],
  'out_of_scope': ['Full payment rail orchestration (see payment-processing doc)',
                   'Merchant dashboard UI',
                   'Real-time analytics warehouse (batch export only MVP)',
                   'Multi-master active-active writers on same transaction home'],
  'nfr': [('Write latency', 'Sync on checkout path', 'p50 < 25ms, p99 < 120ms in-region'),
          ('Read latency', 'Dashboard + polling', 'p99 < 150ms RYW from home'),
          ('Durability', 'Accepted write ⇒ log entry', 'Quorum commit before ACK'),
          ('Availability', 'High for writes', '99.99% home cell; degrade list reads'),
          ('Idempotency retention', 'Years for money-adjacent', 'Never 24h-only TTL'),
          ('Audit retention', 'Compliance forever', 'Hot months + cold object store'),
          ('Multi-region', 'AA edge, SW home', 'Directory + epoch fencing'),
          ('Scale', '1000× headroom', 'See progressive table')],
  'happy_paths': ['Merchant POST create with Idempotency-Key → log APPEND CREATED → 200 + '
                  'transaction.',
                  'Retry same key + body → 200 + original (no second log entry).',
                  'Capture transition → log APPEND CAPTURED → outbox → webhook + ledger journal.',
                  'GET after POST from home cell → RYW consistent status.',
                  'List with cursor → stable ordering by `(created_at, id)`.',
                  'Cancel authorized-only txn → log APPEND CANCELLED; no capture side effects.'],
  'edge_cases': [('Duplicate key, same body', '200 + stored response; single log sequence'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retries → idempotent return'),
                 ('PATCH with stale version', '409 conflict; client refreshes'),
                 ('Illegal state transition', '400 invalid_request; no log append'),
                 ('Regional failover mid-write', 'Fence epoch; replay outbox; recon window'),
                 ('Hot merchant write storm', 'Shard by merchant; serialize per txn id'),
                 ('Log compaction request', 'Reject — append-only forever; archive old partitions'),
                 ('Cross-region read without home',
                  '503 or stale with `livemode` header — document policy'),
                 ('Ledger post fails after log commit', 'Outbox retry; recon break if exhausted')],
  'scale_rows': [('Merchants', '50K', '500K', '5M', '50M'),
                 ('Peak **write** QPS', '500', '5K', '50K', '500K'),
                 ('Peak **read** QPS', '5K', '50K', '500K', '5M'),
                 ('Log entries / day', '10M', '100M', '1B', '10B'),
                 ('Avg log entry size', '800 B', '—', '—', '—'),
                 ('Idempotency hot keys', '100K active', '1M', '10M', '100M'),
                 ('Audit export jobs / day', '20', '100', '500', '2K'),
                 ('Regional home cells', '2', '3', '6', '12+')],
  'scale_forces': {'10x': 'Partition log by merchant_id; idempotency sharded KV + SQL unique; '
                          'outbox for webhooks.',
                   '100x': 'Directory service; dedicated cells for top merchants; CQRS read models '
                           'from log stream.',
                   '1000x': 'Time+merchant log partitions; regional homes sticky; sampled debug '
                            'logs; archive tier automatic.'},
  'constraints': ['Log entries are **immutable** — corrections are compensating append entries.',
                  'Integer minor units on all amount fields.',
                  'API errors typed: `invalid_request_error`, `idempotency_error`, `api_error`.',
                  'Exactly-once **effect** via idempotency — not one HTTP request in access logs.'],
  'estimation': {'traffic': '10M log entries/day ÷ 86400 ≈ 115/s average; peak ~500/s at baseline.',
                 'storage': '10M × 800 B ≈ 8 GB/day baseline; 1000× ≈ 8 TB/day (unit-check: not '
                            'PB).',
                 'bandwidth': '5 KB req/resp × 500K write/s at 1000× ≈ 2.5 GB/s → regional cells.',
                 'memory': 'Hot idempotency: peak_write × 3600s window × 400 B — shard across '
                           'cells.',
                 'bottlenecks': 'Idempotency uniqueness · log append throughput · hot merchant '
                                'shard · outbox fanout',
                 'extra': 'Read:write often 10:1; split list queries to read replicas with lag '
                          'bound.'},
  'entities': 'Transaction, TransactionLogEntry, IdempotencyRecord, Merchant, StateTransition, '
              'AuditEnvelope, OutboxEvent',
  'invariant': 'Accept ⇒ durable log append before client ACK; same `(merchant_id, '
               'Idempotency-Key)` → one economic transition sequence',
  'deal_breakers': [('Mutate log rows in place', 'Audit broken; retries unsafe'),
                    ('ACK before durable log commit', 'Ghost transactions in API'),
                    ('Delete transaction history', 'Compliance failure'),
                    ('Multi-master writers per transaction home', 'Split-brain state transitions'),
                    ('Skip idempotency on capture/refund', 'Double economic effect')],
  'apis': ['POST /v1/transactions',
           'GET /v1/transactions/{id}',
           'GET /v1/transactions',
           'POST /v1/transactions/{id}/cancel',
           'POST /v1/transactions/{id}/capture'],
  'protocols': 'Idempotent write: auth → validate → BEGIN → upsert idempotency PROCESSING → append '
               'log + update resource → outbox → COMPLETE → COMMIT → ACK. Reads route to home cell '
               'for RYW.',
  'hld_sections': '### 3.4 Transaction log as source of truth\n'
                  '\n'
                  '```text\n'
                  'transactions(id, merchant_id, status, amount_minor, currency, version, ...)\n'
                  'transaction_log(\n'
                  '  seq, transaction_id, transition, payload_json, actor, request_id, created_at\n'
                  ')  -- append-only, monotonic seq per transaction_id\n'
                  '\n'
                  'Materialized `status` on transactions row updated in same TX as log append.\n'
                  'Audit replay: rebuild state from log alone.\n'
                  '```\n'
                  '\n'
                  '### 3.5 State transition rules\n'
                  '\n'
                  '| From | Allowed transitions |\n'
                  '|------|---------------------|\n'
                  '| `requires_payment_method` | `requires_confirmation`, `cancelled` |\n'
                  '| `requires_confirmation` | `processing`, `cancelled` |\n'
                  '| `processing` | `succeeded`, `requires_action`, `failed` |\n'
                  '| `succeeded` | `refunded` (partial/full via separate refund API) |\n'
                  '\n'
                  '**Deal-breaker:** skipping validation and writing status directly without log '
                  'entry.\n'
                  '\n'
                  '### 3.6 Pagination & list semantics\n'
                  '\n'
                  'Cursor encodes `(created_at, id)` tuple — stable under concurrent inserts when '
                  'scanning backward in time.\n'
                  'Document whether list is snapshot-isolated or may duplicate/miss under extreme '
                  'churn.\n'
                  '\n'
                  '### 3.7 Ledger integration\n'
                  '\n'
                  '```text\n'
                  'On transition → SUCCEEDED (capture):\n'
                  '  outbox → ledger.PostJournal(journal_key=txn_id + ":capture:v1")\n'
                  'If ledger returns duplicate → treat success (already posted)\n'
                  'Never post ledger before local log commit\n'
                  '```',
  'diagrams': '### 4.1 End-to-end\n'
              '\n'
              '```text\n'
              'Merchant SDK / Internal Services\n'
              '        |\n'
              '        v\n'
              '   API Gateway (AA, rate limit, auth)\n'
              '        |\n'
              '        v\n'
              ' Transaction API Service\n'
              '        |\n'
              '        v\n'
              ' Directory → merchant_id → home cell\n'
              '        |\n'
              '        v\n'
              ' Home Cell\n'
              '   |-- transactions + transaction_log (append)\n'
              '   |-- idempotency store\n'
              '   |-- outbox → webhooks / ledger worker\n'
              '        |\n'
              '        +--> Read replicas (list/search)\n'
              '        +--> Archive / warehouse export\n'
              '```\n'
              '\n'
              '### 4.2 Sequence: create transaction\n'
              '\n'
              '```text\n'
              'Client → POST /transactions (Idempotency-Key)\n'
              'Home → idempotency upsert PROCESSING\n'
              '     → INSERT transaction + log[CREATED]\n'
              '     → outbox transaction.created\n'
              '     → idempotency COMPLETE\n'
              '     → COMMIT\n'
              'Client ← 201 Transaction\n'
              'Retry → same response, seq unchanged\n'
              '```\n'
              '\n'
              '### 4.3 Sequence: capture + ledger\n'
              '\n'
              '```text\n'
              'Client → POST /transactions/{id}/capture\n'
              'Home → validate state machine\n'
              '     → log[CAPTURED] + status update (same TX)\n'
              '     → outbox → LedgerWorker\n'
              'LedgerWorker → PostJournal(journal_key=...)\n'
              '             → mark outbox published\n'
              'WebhookWorker → delivery at-least-once\n'
              '```\n'
              '\n'
              '### 4.4 Sequence: regional failover\n'
              '\n'
              '```text\n'
              'Cell A fenced epoch N\n'
              'Cell B promoted N+1\n'
              'Replay A outbox gap\n'
              'Recon: log seq vs ledger journals for window\n'
              'Resume writes when break count below threshold\n'
              '```\n'
              '\n'
              '### 4.5 Sequence: list with cursor\n'
              '\n'
              '```text\n'
              'Client → GET /transactions?starting_after=txn_abc\n'
              'Edge → read replica or home (policy)\n'
              '     → index scan (merchant_id, created_at, id)\n'
              '     ← page + has_more + next_cursor\n'
              '```',
  'deep_sections': [('5.10 Log immutability & compensating entries',
                     'Corrections never UPDATE log rows. A mistaken capture is reversed by '
                     'appending `REVERSED` with link to original seq.\n'
                     'Recon replays log to verify materialized status matches derived state.\n'
                     'Property test: ∀ txn, fold(log entries) == resource.status.'),
                    ('5.11 Optimistic concurrency on PATCH',
                     'Clients send `If-Match: version` or `version` field.\n'
                     'Server rejects if version stale — prevents lost updates on metadata fields '
                     '(description, metadata map).\n'
                     'Money fields may be immutable after create — policy explicit.'),
                    ('5.12 API versioning & expand/contract',
                     'Add nullable fields first → backfill → enforce.\n'
                     'Old clients ignore unknown fields; new clients require new version header.\n'
                     'Deprecation: sunset header + metric on old version usage.'),
                    ('5.13 Hot merchant isolation',
                     'Top merchants get dedicated home cell or sub-shard.\n'
                     'Per-transaction_id serialization prevents cross-txn ordering issues while '
                     'allowing parallel txns.'),
                    ('5.14 Read replica lag policy',
                     'Money status checks for payout gates: RYW from primary.\n'
                     'Dashboard lists: OK up to 30s lag with `as_of` timestamp in response.'),
                    ('5.15 Log export for warehouse',
                     'CDC stream from log table → Kafka → warehouse.\n'
                     'Ordering key = transaction_id; consumers idempotent on seq.')],
  'wrapup_decisions': [('Log model', 'Append-only transaction_log + materialized resource'),
                       ('Idempotency', 'Merchant-scoped key + body hash; long retention'),
                       ('Reads', 'RYW via home; replica for lists with lag bound'),
                       ('Async', 'Transactional outbox to webhooks + ledger'),
                       ('Multi-region', 'AA edge; SW home per merchant shard')],
  'wrapup_risks': ['Log/table drift if materialized update bugs',
                   'Stuck PROCESSING idempotency under crash',
                   'Hot merchant shard contention',
                   'Ledger outbox lag causing recon breaks',
                   'API version migration mistakes'],
  'interview_plan': [('0–5', 'Scope: API + log, not full payments rail'),
                     ('5–15', 'Entities, state machine, idempotency protocol'),
                     ('15–25', 'Log immutability, outbox, ledger tie-in'),
                     ('25–35', 'Multi-region, failover, read paths'),
                     ('35–45', 'Scale table, pagination, deal-breakers')],
  'qa_pairs': [('Why append-only log vs update row?',
                'Audit and replay; disputes need history; corrections are explicit transitions.'),
               ('How long retain idempotency keys?',
                'Years or forever for capture/refund — not 24h.'),
               ('Same key different body?', '409 — client bug; never silently merge.'),
               ('Can list API miss new txns?',
                'Possible under replica lag — document; use RYW GET for critical checks.'),
               ('When post to ledger?',
                'After local log commit on economic transition; journal_key ties to txn id.'),
               ('Exactly-once webhooks?',
                'No — at-least-once with stable event_id; merchant dedupes.'),
               ('How handle 1000× write QPS?',
                'Shard by merchant; partition log; async ledger via outbox.'),
               ('PATCH vs POST for transitions?',
                'POST for state transitions (explicit); PATCH for metadata only.'),
               ('Float amounts?', 'Never — integer minor units.'),
               ('Integration round vs this?',
                'Integration = code against docs; this = HLD of API+log service.'),
               ('PROCESSING stuck?', 'Sweeper + inquiry whether log seq committed; never new key.'),
               ('Cross-region read?', 'Analytics OK stale; payout gates need home RYW.'),
               ('Delete GDPR request?',
                'Pseudonymize metadata; retain log hash chain for audit policy — legal review.'),
               ('Cursor pagination vs offset?', 'Cursor — offset breaks under concurrent inserts.'),
               ('Dark launch?',
                'Shadow compare log-derived status vs legacy table before cutover.'),
               ('What breaks first at 10×?', 'Idempotency store — shard + SQL unique backing.'),
               ('Log compaction?', 'Never delete — archive to cold tier with legal hold.'),
               ('Typed errors on retry?',
                'Same outcome must return same HTTP status on idempotent replay.')],
  'schema': 'transactions(\n'
            '  id, merchant_id, status, amount_minor, currency, version,\n'
            '  metadata_json, created_at, updated_at\n'
            ')\n'
            'transaction_log(\n'
            '  seq BIGSERIAL, transaction_id, transition, payload_json,\n'
            '  actor, request_id, created_at\n'
            ')\n'
            'UNIQUE(transaction_id, seq)\n'
            'idempotency(merchant_id, key, request_hash, status, response_json, ...)\n'
            'outbox(id, topic, payload, created_at, published_at)',
  'api_sketch': 'POST /v1/transactions\n'
                'Headers: Idempotency-Key, Stripe-Version: 2024-06-20\n'
                '{ "amount": 2000, "currency": "usd", "capture_method": "manual" }\n'
                '→ 201 { "id": "txn_1", "status": "requires_confirmation", ... }\n'
                '\n'
                'POST /v1/transactions/txn_1/capture\n'
                '→ 200 { "status": "succeeded", ... }',
  'state_machine': 'requires_payment_method → requires_confirmation → processing → succeeded | '
                   'failed | cancelled',
  'pseudocode': 'function createTransaction(req):\n'
                '  return home(merchant).tx:\n'
                '    idem = upsertIdempotency(req.key, hash(req.body))\n'
                '    if idem.complete: return idem.response\n'
                '    txn = insertTransaction(req)\n'
                '    appendLog(txn.id, CREATED, req)\n'
                '    outbox.emit(transaction.created, txn)\n'
                '    return completeIdempotency(txn)',
  'glossary': [('Transaction log', 'Append-only sequence of state transitions per transaction'),
               ('RYW', 'Read-your-writes — GET after POST sees own write'),
               ('Transition', 'Named state change appended to log'),
               ('Materialized status', 'Cached current state derived from log')],
  'related': 'payment-processing, idempotent-payment-processing, ledger-bookkeeping, '
             'webhook-delivery'},
 {'file': 'internal-authorization-system-design.md',
  'title': 'Internal Authorization System',
  'focus': 'RBAC+ABAC · PDP/PEP · Audit · Break-glass',
  'scope': 'Design internal authorization from ~50K checks/s to 1000x fail-closed.',
  'goal': 'bound internal **authz**—PEP/PDP, policy-as-data, cache, audit.',
  'functional_reqs': [('Subject?', 'Service+mTLS', 'Principal ID'),
                      ('Policy?', 'RBAC+ABAC versioned', 'Policy store'),
                      ('Default?', 'Deny', 'Fail closed money'),
                      ('Audit?', 'Every decision', 'Append log'),
                      ('Break-glass?', 'TTL grant', 'Dual approve'),
                      ('Cache?', 'TTL+invalidate', 'On revoke'),
                      ('Resources?', 'Journals payouts', 'Hierarchy'),
                      ('Latency?', 'ms cached', 'Budget eval'),
                      ('Multi-region?', 'Policy replica', 'Version sync'),
                      ('Testing?', 'Policy CI', 'Matrix tests'),
                      ('Rollout?', 'Shadow', 'Compare'),
                      ('PEP?', 'Sidecar', 'Local cache')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'PEP sidecar rollout; Redis decision cache; audit batching.',
                   '100x': 'Sharded PDP read path; sample audit for read-only checks; policy CDN.',
                   '1000x': 'Regional PEP clusters; aggressive cache; compile policies to '
                            'bytecode.'},
  'mvp': ['POST /v1/authz/check',
          'POST /v1/policies',
          'GET /v1/principals/{id}/roles',
          'POST /v1/break-glass/grant',
          'Policy bundle signing and version registry',
          'Decision audit export API'],
  'out_of_scope': ['Customer-facing IAM product',
                   'Per-row SQL grants without PEP',
                   'Real-time ML risk scoring in authz path'],
  'nfr': [('Check latency', 'Hot path per RPC', 'p99 < 5ms cached, < 30ms uncached'),
          ('Failure mode', 'Money mutations', 'Fail closed DENY'),
          ('Policy propagation', 'Revoke global', '< 60s cache invalidation SLO'),
          ('Audit write rate', 'Every decision', 'Sample non-money at 1000×'),
          ('Availability PDP', 'Critical', '99.99% with read replicas'),
          ('Scale', '50K→50M checks/s', 'Shard PDP; PEP cache'),
          ('Consistency', 'Policy version', 'Monotonic published version'),
          ('Security', 'Tamper policy', 'Signed bundles')],
  'happy_paths': ['Payout service PEP → PDP ALLOW → audit → proceed',
                  'Revoked role → version bump → cache invalidate → DENY',
                  'Break-glass dual-approved → temporary ALLOW → auto-expire',
                  'Shadow policy logs WOULD_DENY without blocking',
                  'Cached decision on repeated check → sub-ms',
                  'Cross-region PEP uses local policy replica same version'],
  'edge_cases': [('PDP timeout on journal post', 'DENY fail closed'),
                 ('Stale ALLOW after revoke', 'Version invalidation fanout'),
                 ('Conflicting allow/deny rules', 'Deny-wins precedence explicit'),
                 ('Break-glass past TTL', 'Hard DENY + alert'),
                 ('Principal credential rotated', 'Old token DENY within skew window'),
                 ('Policy eval exceeds budget', 'DENY on sensitive resources'),
                 ('Audit sink full', 'Buffer + fail closed money'),
                 ('Regional replica lag', 'Money DENY if version stale'),
                 ('Policy injection attempt', 'Signature verify reject'),
                 ('PEP bypass direct DB', 'Network policy block + audit')],
  'scale_rows': [('Service principals', '2K', '20K', '200K', '2M'),
                 ('Authz checks / s', '50K', '500K', '5M', '50M'),
                 ('Policy documents', '500', '5K', '50K', '500K'),
                 ('Cached hit rate target', '90%', '93%', '95%', '97%'),
                 ('Audit events / day', '4B', '40B', '400B', '4T sampled'),
                 ('Break-glass / day', '5', '20', '100', '500'),
                 ('PDP regions', '2', '3', '6', '12')],
  'estimation': {'traffic': '50K checks/s × ~500 B ≈ 25 MB/s decision traffic baseline.',
                 'storage': 'Audit 4B/day × 200 B ≈ 800 GB/day — tier to cold in hours.',
                 'bandwidth': 'Policy bundle push ~MB on version change infrequent.',
                 'memory': 'PEP cache 50M entries × 64 B impossible — LRU hot principals only.',
                 'bottlenecks': '1. Uncached eval CPU 2. Audit write amp 3. Invalidation fanout 4. '
                                'Policy complexity',
                 'extra': 'Separate money PEP (strict timeout) from analytics PEP.'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Policy-as-data model\n'
                  '\n'
                  'Policies stored as signed JSON/RegO bundles with monotonic `policy_version`.\n'
                  'Services embed **no** authorization rules in application code — only PEP '
                  'calls.\n'
                  '\n'
                  '### 3.12 PEP / PDP separation\n'
                  '\n'
                  '```text\n'
                  'PEP (sidecar): extract (principal, action, resource) → cache → PDP → audit\n'
                  'PDP (stateless pool): load policy version → evaluate → return ALLOW/DENY + '
                  'obligations\n'
                  '```\n'
                  '\n'
                  '### 3.13 Break-glass workflow\n'
                  '\n'
                  'Dual approver via ticketing integration → `break_glass_grants` row → PDP '
                  'injects temporary rule → max TTL 4h → page SecOps → enhanced audit.\n'
                  '\n'
                  '### 3.14 Fail-closed matrix\n'
                  '\n'
                  '| Path | PDP down | Timeout |\n'
                  '|------|----------|---------|\n'
                  '| Post journal / payout | DENY | DENY |\n'
                  '| Read dashboard analytics | DENY or cached ALLOW (flag) | Short cache only |\n',
  'diagrams': '### 4.1 End-to-end\n'
              '\n'
              '```text\n'
              'Microservices → PEP sidecar → Decision cache → PDP cluster → Policy Store '
              '(versioned)\n'
              '                                    ↓\n'
              '                              Audit Log (immutable)\n'
              '```\n'
              '\n'
              '### 4.2 Allow check (cache miss)\n'
              '\n'
              'Service RPC → PEP intercept → cache miss → PDP eval v42 → ALLOW → cache 60s → audit '
              '→ proceed\n'
              '\n'
              '### 4.3 Revoke propagation\n'
              '\n'
              'Admin removes role → policy v43 published → pub/sub `invalidate(principal_id)` → '
              'all PEPs drop cache entries\n'
              '\n'
              '### 4.4 Break-glass\n'
              '\n'
              'Ticket approved ×2 → POST /break-glass/grant → PDP includes temp rule → expires → '
              'DENY resumes\n'
              '\n'
              '### 4.5 Regional failure\n'
              '\n'
              'US-East PDP degraded → PEP uses replica policy read-only same version → if stale '
              'version → money DENY\n',
  'deep_sections': [('5.10 ABAC attribute pipeline',
                     'Fetch merchant_tier, env, cell_id from directory with 30s cache. Missing '
                     'attribute → DENY on sensitive actions.'),
                    ('5.11 Policy compilation',
                     'Compile RegO to WASM for fast eval; cache compiled artifact per '
                     'policy_version.'),
                    ('5.12 Decision audit sampling',
                     '100% money mutations; 1% sample read-only checks at 1000× to control cost.'),
                    ('5.13 Shadow policy rollout',
                     'Run v43 shadow alongside v42; log decision diffs; zero user impact until '
                     'cutover.'),
                    ('5.14 Obligations pattern',
                     'ALLOW may carry obligations: mask_fields, require_dual_control — PEP '
                     'enforces downstream.'),
                    ('5.15 Cross-service delegation tokens',
                     'Narrow JWT: action=read, resource=journal/123, TTL 5m — PDP validates '
                     'chain.')],
  'wrapup_decisions': [('Model', 'RBAC+ABAC policy-as-data signed'),
                       ('Eval', 'PEP cache + PDP pool'),
                       ('Failure', 'Fail closed money'),
                       ('Audit', 'Every decision with version'),
                       ('Break-glass', 'Dual control TTL')],
  'wrapup_risks': ['Stale cache after revoke',
                   'PDP overload cascade',
                   'Policy complexity regression',
                   'Break-glass abuse',
                   'Audit cost at 1000×'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Fail open or closed?', 'Closed for money; configurable read-only.'),
               ('Cache invalidation?', 'Policy version bump + pub/sub by principal prefix.'),
               ('50M checks/s?', 'Shard PDP; PEP cache; sample audit.'),
               ('ABAC vs RBAC?', 'Both — roles coarse, attributes fine.'),
               ('Break-glass?', 'Dual approve, TTL, enhanced audit.'),
               ('Service mesh?', 'PEP as ext_authz filter.'),
               ('Policy rollback?', 'Revert version pointer; invalidate all caches.'),
               ('Deny default?', 'Yes explicit allow only.'),
               ('Audit tamper?', 'Hash chain to immutable store.'),
               ('Integration access mgmt?', 'Human roles synced; machines separate.'),
               ('Latency budget?', '5ms cached 30ms uncached.'),
               ('Trap ACL in code?', 'Policy-as-data.'),
               ('Trap fail open outage?', 'Never payouts.'),
               ('Shadow mode?', 'Log diffs pre-cutover.'),
               ('Cross-region?', 'Replicate policy; version sync.'),
               ('Principal types?', 'Service mTLS vs human SSO.'),
               ('Obligations?', 'ALLOW with conditions enforced by PEP.'),
               ('Policy testing?', 'CI matrix per bundle.'),
               ('Seccomp bypass?', 'Network deny direct data plane.'),
               ('Retention?', 'Years immutable audit.')],
  'schema': 'policies(id, version, body, signature, published_at)\n'
            'principals(id, type, attrs_json)\n'
            'role_bindings(principal_id, role, scope)\n'
            'authz_decisions(id, principal, action, resource, decision, policy_version, '
            'inputs_hash, ts)\n'
            'break_glass_grants(id, principal, approvers, reason, expires_at)',
  'api_sketch': 'POST /v1/authz/check\n'
                '{ principal: svc_payments, action: post_journal, resource: book/mer_1 }\n'
                '→ { allowed: true, policy_version: 42 }',
  'state_machine': 'PolicyVersion: draft → published → deprecated; Grant: active → expired',
  'pseudocode': 'function check(p,a,r):\n'
                '  k=cacheKey(p,a,r,currentPolicyVersion)\n'
                '  if hit: return hit\n'
                '  d=pdp.eval(p,a,r,currentPolicyVersion)\n'
                '  audit(p,a,r,d); cache.set(k,d,ttl); return d',
  'glossary': [('PEP', 'Policy Enforcement Point — local to service'),
               ('PDP', 'Policy Decision Point — central evaluator'),
               ('ABAC', 'Attribute-based access control'),
               ('Break-glass', 'Emergency time-boxed grant')],
  'related': 'access-management, ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Internal Authorization System: regional failover',
                        'body': 'For Internal Authorization System, fence home epoch, replay '
                                'outbox, run recon, resume when breaks clear — domain-specific '
                                'invariants in section 3.'},
                       {'title': 'Internal Authorization System: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Internal Authorization System: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Internal Authorization System: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Internal Authorization System: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Internal Authorization System — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Internal Authorization System — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'rate-limiter-system-design.md',
  'title': 'Rate Limiter',
  'focus': 'Token bucket · Sliding window · Distributed counters · Edge+central',
  'scope': 'Design distributed rate limiter ~100K decisions/s to 1000x fair per tenant.',
  'goal': 'bound **rate limiting** for Stripe APIs—algorithms, distribution, fairness, fail-closed '
          'money routes.',
  'functional_reqs': [('Keys?', 'API key+IP+route', 'Composite key'),
                      ('Algorithm?', 'Token bucket+sliding', 'Hybrid'),
                      ('Burst?', 'Allow N burst', 'Configurable'),
                      ('Distributed?', 'Edge+central reconcile', 'Eventual fair'),
                      ('Money routes?', 'Fail closed if uncertain', '429 not unlimited'),
                      ('Overrides?', 'Support plans', 'Quota admin API'),
                      ('Response?', '429 Retry-After', 'Headers'),
                      ('Multi-region?', 'Local counters sync', 'Merge windows'),
                      ('Accuracy?', '~exact per key', 'Not global single counter'),
                      ('Observability?', 'Usage metrics', 'Per tenant'),
                      ('Testing?', 'Load test fairness', 'Noisy neighbor'),
                      ('Rollout?', 'Shadow limit', 'Compare 429 rate')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['Internal allow(key,cost) at edge',
          'POST /v1/limits/rules admin',
          'GET /v1/limits/usage/{tenant}',
          'Token bucket + sliding window hybrid',
          'Per-route override API',
          'Usage metrics export'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Rate Limiter design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Keys? → API key+IP+route → durable write + audit',
                  'Algorithm? → Token bucket+sliding → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Money routes? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': '100K decisions/s baseline API edge',
                 'storage': 'Counter state ephemeral+snapshots',
                 'bandwidth': 'Minimal 100B/decision',
                 'memory': 'Token state per key sharded',
                 'bottlenecks': 'Hot API key, sync lag edge-central',
                 'extra': 'Money routes 429 when limiter unavailable'},
  'entities': 'LimitRule, CounterShard, TokenBucketState, Decision, Override, QuotaPlan',
  'invariant': 'Money-critical routes return 429 when limiter uncertain—never fail open unlimited',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['Internal: allow(key,cost)', 'POST /v1/limits/rules', 'GET /v1/limits/usage/{tenant}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Rate Limiter)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Rate Limiter — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Rate Limiter)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Rate Limiter API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.'),
               ('Token bucket vs sliding window?',
                'Bucket for burst; sliding for strict RPM contracts — hybrid common.'),
               ('Global counter Redis?', 'No at scale — shard by hash(key) mod N.'),
               ('Token bucket vs sliding window?',
                'Bucket for burst; sliding for strict RPM contracts — hybrid common.'),
               ('Global counter Redis?', 'No at scale — shard by hash(key) mod N.'),
               ('Token bucket vs sliding window?',
                'Bucket for burst; sliding for strict RPM contracts — hybrid common.'),
               ('Global counter Redis?', 'No at scale — shard by hash(key) mod N.'),
               ('Token bucket vs sliding window?',
                'Bucket for burst; sliding for strict RPM contracts — hybrid common.'),
               ('Global counter Redis?', 'No at scale — shard by hash(key) mod N.'),
               ('Token bucket vs sliding window?',
                'Bucket for burst; sliding for strict RPM contracts — hybrid common.'),
               ('Global counter Redis?', 'No at scale — shard by hash(key) mod N.'),
               ('Token bucket vs sliding window?',
                'Bucket for burst; sliding for strict RPM contracts — hybrid common.'),
               ('Global counter Redis?', 'No at scale — shard by hash(key) mod N.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'transaction-apis-log, metrics-service, payment-processing',
  'interview_probes': [{'title': 'Edge vs central drift',
                        'body': 'Document conservative merge rule for money APIs when counters '
                                'disagree.'},
                       {'title': 'Celebrity merchant key',
                        'body': 'Shard counter into sub-keys or local token borrow with central '
                                'reconciliation.'}],
  'extra_appendix': '### 8.19 Rate Limiter — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Rate Limiter — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'metrics-service-system-design.md',
  'title': 'Metrics Service',
  'focus': 'Time-series · Cardinality control · Rollups · Query · Retention',
  'scope': 'Design internal metrics platform ~500K samples/s to 1000x cardinality-safe.',
  'goal': 'bound **metrics ingestion and query**—cardinality, rollups, tenant isolation.',
  'functional_reqs': [('Emitters?', 'SDK sidecars', 'Auth per service'),
                      ('Types?', 'Counter gauge histogram', 'Typed agg'),
                      ('Labels?', 'Low cardinality', 'Governor deny'),
                      ('Query?', 'Range queries dashboards', 'Query engine'),
                      ('Retention?', 'Raw short rollups long', 'Tiered'),
                      ('Multi-tenant?', 'Team isolation', 'Quotas'),
                      ('Exactness?', 'Billing stricter', 'Separate path'),
                      ('Alerts?', 'Threshold rules', 'Eval service'),
                      ('Late data?', 'Watermark window', 'Bound lateness'),
                      ('Fan-in?', 'Cross-cell agg', 'Hierarchy'),
                      ('Registry?', 'Metric names', 'Governance'),
                      ('API?', 'Write+query HTTP', 'Versioned')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/metrics/write batch ingest',
          'POST /v1/query/range PromQL-like',
          'Cardinality governor at ingest',
          'Rollups 1m/5m/1h automatic',
          'Tenant quota enforcement',
          'Alert rule evaluation hook'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Metrics Service design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['SDK batch push → ingest validate labels → TSDB write',
                  'High-cardinality label rejected at edge → 400 metric_rejected',
                  'Query range → rollup tier selected by time span',
                  'Late sample within watermark → accepted into window',
                  'Cross-cell fan-in → hierarchical aggregator',
                  'Billing counter exact path separate from analytics HLL'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Samples/s', '500K', '5M', '50M', '500M'),
                 ('Active series', '10M', '100M', '1B', '10B'),
                 ('Query QPS', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'MetricSeries, Sample, LabelSet, Rollup, QueryPlan, RetentionPolicy',
  'invariant': 'Ingest never blocks payment hot path; cardinality limits enforced at edge',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/metrics/write', 'POST /v1/query/range', 'GET /v1/series'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Metrics Service)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Metrics Service — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Metrics Service)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Metrics Service API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'distributed-metrics-counter, apm-system-design, rate-limiter',
  'interview_probes': [{'title': 'Cardinality explosion',
                        'body': 'Reject label value >10K per metric; alert owner; never silently '
                                'drop without metric.'},
                       {'title': 'Query timeout at 1000×',
                        'body': 'Downsample automatically; return partial with warning header.'}],
  'extra_appendix': '### 8.19 Metrics Service — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Metrics Service — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'distributed-lru-cache-system-design.md',
  'title': 'Distributed LRU Cache',
  'focus': 'Consistent hash · Leases · Invalidation · Hot keys',
  'scope': 'Design distributed LRU cache ~200K get/s; never SoT for money balances.',
  'goal': 'bound **distributed cache**—eviction, consistency hints, hot keys, money read policy.',
  'functional_reqs': [('Use case?', 'Read-heavy internal', 'Not money SoT'),
                      ('Eviction?', 'LRU per shard', 'Memory cap'),
                      ('Routing?', 'Consistent hash', 'Virtual nodes'),
                      ('Invalidation?', 'Pub/sub lease', 'Version bump'),
                      ('TTL?', 'Per key class', 'Short money hints'),
                      ('Hot key?', 'Replica fanout', 'Detect skew'),
                      ('Stale?', 'Explicit SLO', 'Bypass for payout'),
                      ('Multi-region?', 'Regional replicas', 'No active-active write'),
                      ('Size limit?', 'Max entry bytes', 'Reject huge'),
                      ('Near cache?', 'Local L1', 'Combined L2'),
                      ('Warmup?', 'On deploy', 'Gradual'),
                      ('Observability?', 'Hit rate evictions', 'Per shard')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Distributed LRU Cache',
          'Admin recon/replay hooks for Distributed LRU Cache',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Distributed LRU Cache design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Use case? → Read-heavy internal → durable write + audit',
                  'Eviction? → LRU per shard → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'TTL? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Distributed LRU Cache)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Distributed LRU Cache — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Distributed LRU Cache)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Distributed LRU Cache API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Distributed LRU Cache: regional failover',
                        'body': 'For Distributed LRU Cache, fence home epoch, replay outbox, run '
                                'recon, resume when breaks clear — domain-specific invariants in '
                                'section 3.'},
                       {'title': 'Distributed LRU Cache: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Distributed LRU Cache: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Distributed LRU Cache: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Distributed LRU Cache: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Distributed LRU Cache — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Distributed LRU Cache — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'apm-system-design.md',
  'title': 'Application Performance Monitoring',
  'focus': 'Tracing · Sampling · Service map · PII scrub · SLOs',
  'scope': 'Design APM ~50K spans/s to 1000x with head/tail sampling.',
  'goal': 'bound **distributed tracing APM**—sampling, storage tiers, PII, SLO dashboards.',
  'functional_reqs': [('Spans?', 'HTTP+RPC auto', 'SDK inject'),
                      ('Sampling?', 'Head+tail error bias', 'Keep errors'),
                      ('Storage?', 'Hot+cold traces', 'Retention tiers'),
                      ('PII?', 'Scrub rules', 'No secrets in tags'),
                      ('Service map?', 'Edge aggregation', 'Dependency graph'),
                      ('Query?', 'Trace by id latency', 'Indexed'),
                      ('Critical path?', 'Never block request', 'Async export'),
                      ('Cardinality?', 'Limit tag keys', 'Deny high'),
                      ('SLO?', 'Latency error budget', 'Dashboards'),
                      ('Multi-region?', 'Regional collectors', 'Global query federate'),
                      ('Alerts?', 'Tail sample anomalies', 'Page on SLO burn'),
                      ('Rollout?', 'SDK version', 'Feature flag')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Application Performance Monitoring',
          'Admin recon/replay hooks for Application Performance Monitoring',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Application Performance '
                   'Monitoring design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Spans? → HTTP+RPC auto → durable write + audit',
                  'Sampling? → Head+tail error bias → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Service map? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Application Performance Monitoring)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Application Performance Monitoring — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Application Performance Monitoring)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Application Performance Monitoring API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Application Performance Monitoring: regional failover',
                        'body': 'For Application Performance Monitoring, fence home epoch, replay '
                                'outbox, run recon, resume when breaks clear — domain-specific '
                                'invariants in section 3.'},
                       {'title': 'Application Performance Monitoring: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Application Performance Monitoring: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Application Performance Monitoring: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Application Performance Monitoring: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Application Performance Monitoring — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Application Performance Monitoring — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'data-platform-sharding-system-design.md',
  'title': 'Production Data Platform Sharding',
  'focus': 'Shard keys · Directory · Reshard · Dual-write',
  'scope': 'Design OLTP sharding ~100K row writes/s zero-downtime resharding.',
  'goal': 'bound **database sharding platform**—directory, migration, query routing.',
  'functional_reqs': [('Shard key?', 'Stable high cardinality', 'tenant_id etc'),
                      ('Directory?', 'SoT routing', 'Epoch fencing'),
                      ('Reshard?', 'Dual-write range move', 'Verify backfill'),
                      ('Cross-shard query?', 'Avoid hot path', 'Scatter-gather async'),
                      ('Analytics?', 'Replicas/warehouse', 'Not primary OLTP'),
                      ('Split?', 'Range or hash', 'Plan capacity'),
                      ('Rollback?', 'Directory pointer revert', 'Dual-write window'),
                      ('Consistency?', 'Single-shard TX', 'No 2PC hot path'),
                      ('Observability?', 'Shard heat', 'Rebalance jobs'),
                      ('Tenant move?', 'Planned migration', 'Maintenance window optional'),
                      ('Global indexes?', 'Async', 'Not synchronous'),
                      ('Testing?', 'Shadow routing', 'Compare rows')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Production Data Platform Sharding',
          'Admin recon/replay hooks for Production Data Platform Sharding',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Production Data Platform '
                   'Sharding design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Shard key? → Stable high cardinality → durable write + audit',
                  'Directory? → SoT routing → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Analytics? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Production Data Platform Sharding)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Production Data Platform Sharding — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Production Data Platform Sharding)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Production Data Platform Sharding API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Production Data Platform Sharding: regional failover',
                        'body': 'For Production Data Platform Sharding, fence home epoch, replay '
                                'outbox, run recon, resume when breaks clear — domain-specific '
                                'invariants in section 3.'},
                       {'title': 'Production Data Platform Sharding: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Production Data Platform Sharding: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Production Data Platform Sharding: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Production Data Platform Sharding: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Production Data Platform Sharding — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Production Data Platform Sharding — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'payment-processing-system-design.md',
  'title': 'End-to-End Payment Processing',
  'focus': 'PaymentIntent · Rails · 3DS · Ledger · Recon',
  'scope': 'Design payment processing ~1K QPS to 1000x idempotent lifecycle.',
  'goal': 'bound **end-to-end payments**—PaymentIntent, rails, ledger, uncertain windows.',
  'functional_reqs': [('Lifecycle?', 'Create confirm capture refund', 'State machine'),
                      ('Idempotency?', 'All mutating APIs', 'Long retention'),
                      ('Rails?', 'Card ACH etc', 'Orchestrator'),
                      ('3DS?', 'requires_action', 'Async resume'),
                      ('Ledger?', 'Journal on capture', 'journal_key'),
                      ('Webhooks?', 'Outbox events', 'Merchant notify'),
                      ('Disputes?', 'Hook reserve', 'Out of MVP depth OK'),
                      ('Multi-currency?', 'Integer minor', 'No float'),
                      ('Recon?', 'Rail vs internal', 'Daily breaks'),
                      ('Partial capture?', 'Amount <= authorized', 'Multiple captures policy'),
                      ('Cancel?', 'Void uncaptured', 'Terminal state'),
                      ('Regional?', 'Home per payment', 'SW cell')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/payment_intents — create with idempotency',
          'POST /v1/payment_intents/{id}/confirm — handle 3DS continuation',
          'POST /v1/payment_intents/{id}/capture — partial/full capture',
          'POST /v1/refunds — idempotent refund against charge',
          'Rail orchestration with uncertain outcome classification',
          'Ledger journal on confirmed economic transition'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one End-to-End Payment Processing '
                   'design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Create PaymentIntent → requires_confirmation → confirm → processing → succeeded',
                  '3DS requires_action → client completes → resume same intent id',
                  'Capture with Idempotency-Key → rail success → ledger journal → webhook',
                  'Duplicate capture key → 200 original charge (no double)',
                  'Refund idempotent → ledger reversing journal linked',
                  'Rail timeout → inquiry → classify → no blind retry new key'],
  'edge_cases': [('Duplicate capture key', '200 stored charge'),
                 ('Capture > authorized', '400 invalid amount'),
                 ('Confirm after cancel race', '409 state conflict TX'),
                 ('Rail timeout ambiguous', 'Mark requires_inquiry; worker polls rail'),
                 ('Partial capture sum > auth', 'Reject or policy split captures'),
                 ('3DS abandon', 'Intent expires requires_action → failed/cancelled'),
                 ('Currency mismatch', '400 before rail call'),
                 ('Ledger post fails', 'Outbox retry; payment stays succeeded; recon'),
                 ('Regional failover', 'Fence home; replay outbox; pause captures policy'),
                 ('Webhook before ledger', 'Never — outbox ordering in TX')],
  'scale_rows': [('Peak payment write QPS', '1K', '10K', '100K', '1M'),
                 ('Peak status read QPS', '10K', '100K', '1M', '10M'),
                 ('Payments / day', '50M', '500M', '5B', '50B'),
                 ('Rail attempts / payment', '1.2', '1.3', '1.5', '1.8'),
                 ('3DS step-up rate', '8%', '10%', '12%', '15%'),
                 ('Merchants', '100K', '1M', '10M', '100M'),
                 ('Home cells', '2', '4', '8', '16')],
  'estimation': {'traffic': '50M payments/day peak ~1K/s',
                 'storage': 'Payment row ~2KB + attempts',
                 'bandwidth': 'Rail payloads regional',
                 'memory': 'Idempotency hot set sharded',
                 'bottlenecks': 'Rail timeout, idempotency, hot merchant, ledger outbox',
                 'extra': '3DS adds async continuation'},
  'entities': 'PaymentIntent, Charge, Refund, RailAttempt, IdempotencyRecord, LedgerJournalRef',
  'invariant': 'One business payment transition per idempotency key; ledger journal_key ties '
               'economic effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/payment_intents', 'POST /v1/payment_intents/{id}/confirm', 'POST /v1/refunds'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 PaymentIntent state machine\n'
                  '\n'
                  '```text\n'
                  'requires_payment_method → requires_confirmation → processing\n'
                  '  → succeeded | requires_action (3DS) → processing | failed | cancelled\n'
                  'Refunds are separate objects linked to Charge, not backward transitions on PI.\n'
                  '```\n'
                  '\n'
                  '### 3.12 Rail orchestration layer\n'
                  '\n'
                  '```text\n'
                  'Orchestrator calls rail with stable idempotency_key per attempt\n'
                  'Timeout → inquiry API with same business key\n'
                  'Never mint new key for same capture intent\n'
                  'Classify: succeeded | failed | indeterminate\n'
                  '```\n'
                  '\n'
                  '### 3.13 Ledger coupling\n'
                  '\n'
                  '```text\n'
                  'On capture succeeded:\n'
                  '  journal_key = payment_intent_id + ":capture:v" + recipe_version\n'
                  '  PostJournal in outbox worker — local PI commit first\n'
                  '```\n'
                  '\n'
                  '### 3.14 Reconciliation\n'
                  '\n'
                  'Daily: sum(captured) vs rail settlement file vs ledger clearing account → open '
                  'breaks.',
  'diagrams': '### 4.1 End-to-end\n'
              '\n'
              '```text\n'
              'Merchant → API Gateway → Payment API → Directory → Home Cell (PI + idempotency)\n'
              '                                              ↓\n'
              '                                    Rail Orchestrator → Card networks\n'
              '                                              ↓\n'
              '                                    Outbox → Ledger / Webhooks / Recon\n'
              '```\n'
              '\n'
              '### 4.2 Confirm + 3DS\n'
              '\n'
              'Client confirm → rail requires 3DS → 200 requires_action + next_action\n'
              'Client completes 3DS → POST confirm again → processing → succeeded\n'
              '\n'
              '### 4.3 Capture idempotent\n'
              '\n'
              'POST capture + Idempotency-Key → TX upsert idem → rail capture → ledger outbox → '
              '200\n'
              '\n'
              '### 4.4 Rail timeout\n'
              '\n'
              'Rail call timeout → mark indeterminate → inquiry worker → same external key → '
              'resolve state\n'
              '\n'
              '### 4.5 Failover\n'
              '\n'
              'Fence cell → promote → replay outbox captures → recon rail window before resume',
  'deep_sections': [('5.10 Partial capture policy',
                     'Multiple captures summing to auth amount; each idempotent; final capture '
                     'closes auth.'),
                    ('5.11 3DS continuation',
                     'Store rail context on PI; resume token ties client retry to same attempt.'),
                    ('5.12 Dispute hooks',
                     'On dispute.opened outbox → reserve hold journal (if in scope).'),
                    ('5.13 Idempotency across confirm/capture',
                     'Separate keys per endpoint; body hash includes amount.'),
                    ('5.14 Rail circuit breaker',
                     'Per rail health; fail fast; route backup rail if configured.'),
                    ('5.15 Merchant level home sharding',
                     'hash(merchant_id) → cell; hot merchant isolated.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('When post ledger?',
                'After local commit on confirmed capture/refund; journal_key ties to PI '
                'transition.'),
               ('Rail timeout handling?',
                'Inquiry with same idempotency key — never blind retry new key.'),
               ('3DS flow?',
                'requires_action is sync API response; async completion via second confirm.'),
               ('Partial capture?', 'Multiple capture calls; track captured_sum ≤ authorized.'),
               ('Refund idempotency?', 'Separate key per refund request; links to charge_id.'),
               ('Exactly-once charge?', 'Idempotency key + rail key + ledger unique journal.'),
               ('Float?', 'Integer minor units only.'),
               ('Active-active capture?', 'No — single-writer home per PI.'),
               ('Webhook ordering?', 'Outbox after DB commit; at-least-once event_id stable.'),
               ('Stuck processing?', 'Sweeper + rail inquiry.'),
               ('Cancel vs refund?', 'Cancel voids uncaptured auth; refund reverses capture.'),
               ('Cross-region read?', 'RYW from home for status; replica OK dashboard lag.'),
               ('Recon break?', 'Open ticket; may pause payouts merchant-level.'),
               ('1000× QPS?', 'Shard merchants; async ledger; rail pool scaling.'),
               ('Integration round?', 'Coding task — not this HLD.'),
               ('Dispute reserve?', 'Ledger hold journal on dispute event.'),
               ('Multiple rails?', 'Orchestrator abstraction; same PI state machine.'),
               ('SCA regulation?', 'requires_action models PSD2 step-up.'),
               ('Client retry 500?', 'Same Idempotency-Key mandatory.'),
               ('Dark launch new rail?', 'Shadow rail call compare before cutover.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'requires_payment_method → requires_confirmation → processing → succeeded | '
                   'requires_action | failed',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, idempotent-payment-processing, webhook-delivery',
  'interview_probes': [{'title': 'Walk through capture retry storm',
                        'body': 'Merchant retries capture 50× same key → one rail call → one '
                                'ledger journal → 50 identical 200 responses.'},
                       {'title': 'Rail succeeds API timeout',
                        'body': 'Worker inquiry finds success → complete idempotency → client '
                                'retry gets 200.'},
                       {'title': 'Hot merchant Black Friday',
                        'body': 'Dedicated cell; rail connection pool; shed noncritical reads.'}],
  'extra_appendix': '### 8.19 PaymentIntent field checklist\n'
                    '\n'
                    '- [ ] amount_capturable vs amount_received tracked separately  \n'
                    '- [ ] last_payment_error populated on failed  \n'
                    '- [ ] next_action for 3DS contains client_secret  \n'
                    '- [ ] metadata size limits enforced  \n'
                    '\n'
                    '### 8.20 Rail attempt log schema\n'
                    '\n'
                    '```text\n'
                    'rail_attempts(id, payment_intent_id, rail, external_idempotency_key,\n'
                    '              status, raw_response_ref, created_at)\n'
                    '```\n'},
 {'file': 'access-management-system-design.md',
  'title': 'Access Management System',
  'focus': 'SSO · SCIM · Dashboard roles · Sessions · MFA',
  'scope': 'Design access mgmt ~10K auth/s for Dashboard and internal tools.',
  'goal': 'bound **identity and access for humans**—SSO, roles, sessions, merchant team ACL.',
  'functional_reqs': [('Users?', 'Merchant team+employees', 'Directory sync'),
                      ('SSO?', 'SAML OIDC', 'Enterprise'),
                      ('Roles?', 'Admin developer etc', 'RBAC dashboard'),
                      ('Sessions?', 'HttpOnly cookies', 'Rotation'),
                      ('MFA?', 'Required admin', 'TOTP/WebAuthn'),
                      ('SCIM?', 'Provision users', 'HR sync'),
                      ('Audit?', 'Login role changes', 'Immutable'),
                      ('API keys?', 'Separate machine creds', 'Rotation policy'),
                      ('Revoke?', 'Global session invalidate', '<60s SLO'),
                      ('Cross-merchant?', 'Strict isolation', 'Never bleed'),
                      ('Break-glass?', 'Internal support', 'Ticket+jump'),
                      ('Compliance?', 'SOC evidence', 'Access reviews')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Access Management System',
          'Admin recon/replay hooks for Access Management System',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Access Management System design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Users? → Merchant team+employees → durable write + audit',
                  'SSO? → SAML OIDC → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'MFA? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Access Management System)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Access Management System — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Access Management System)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Access Management System API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Access Management System: regional failover',
                        'body': 'For Access Management System, fence home epoch, replay outbox, '
                                'run recon, resume when breaks clear — domain-specific invariants '
                                'in section 3.'},
                       {'title': 'Access Management System: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Access Management System: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Access Management System: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Access Management System: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Access Management System — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Access Management System — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'feature-flag-system-design.md',
  'title': 'Feature Flag Service',
  'focus': 'Targeting · Rollouts · Stickiness · Kill switch',
  'scope': 'Design feature flags ~500K eval/s sub-ms cached safe money defaults.',
  'goal': 'bound **feature flag platform**—targeting, sticky buckets, kill switches, audit.',
  'functional_reqs': [('Flags?', 'Boolean multivariate', 'Typed variants'),
                      ('Targeting?', 'Rules on attrs', 'merchant_id env'),
                      ('Rollout?', '% with stickiness', 'Hash subject'),
                      ('Kill switch?', 'Instant off', 'Global flag'),
                      ('Defaults?', 'Safe on outage', 'Money OFF'),
                      ('Audit?', 'Prod changes', 'Who when why'),
                      ('Cache?', 'Edge+local', 'Version poll'),
                      ('Eval latency?', 'Sub-ms cached', 'Budget rule eval'),
                      ('Tenant scope?', 'Per merchant', 'No cross bleed'),
                      ('SDK?', 'Server-side enforce', 'Not client only security'),
                      ('Testing?', 'Override in staging', 'Separate env'),
                      ('Version?', 'Flag config version', 'Monotonic')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Feature Flag Service',
          'Admin recon/replay hooks for Feature Flag Service',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Feature Flag Service design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Flags? → Boolean multivariate → durable write + audit',
                  'Targeting? → Rules on attrs → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Defaults? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Feature Flag Service)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Feature Flag Service — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Feature Flag Service)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Feature Flag Service API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Feature Flag Service: regional failover',
                        'body': 'For Feature Flag Service, fence home epoch, replay outbox, run '
                                'recon, resume when breaks clear — domain-specific invariants in '
                                'section 3.'},
                       {'title': 'Feature Flag Service: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Feature Flag Service: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Feature Flag Service: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Feature Flag Service: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Feature Flag Service — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Feature Flag Service — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'merchant-lending-system-design.md',
  'title': 'Merchant Lending Platform',
  'focus': 'Underwriting · Disbursement · Repayment sweep · Ledger',
  'scope': 'Design merchant lending ~100 events/s with ledger-coupled idempotent money.',
  'goal': 'bound **merchant lending**—loans, disbursement, receivables repayment, ledger.',
  'functional_reqs': [('Underwriting?', 'Risk model decision', 'PII protect'),
                      ('Loan account?', 'Ledger books', 'Dedicated accounts'),
                      ('Disbursement?', 'Idempotent payout', 'journal_key'),
                      ('Repayment?', 'Sweep from captures', 'Hook idempotent'),
                      ('Interest?', 'Accrual schedule', 'Integer minor'),
                      ('Compliance?', 'Reg reporting', 'Audit'),
                      ('Default?', 'Collections state', 'Workflow'),
                      ('Offers?', 'Merchant accept', 'Time bound'),
                      ('Multi-currency?', 'Per loan currency', 'Explicit FX'),
                      ('Limits?', 'Max exposure', 'Platform caps'),
                      ('Recon?', 'Loan balance vs ledger', 'Daily'),
                      ('Regional?', 'Home per loan', 'SW')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Merchant Lending Platform',
          'Admin recon/replay hooks for Merchant Lending Platform',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Merchant Lending Platform '
                   'design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Underwriting? → Risk model decision → durable write + audit',
                  'Loan account? → Ledger books → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Interest? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Merchant Lending Platform)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Merchant Lending Platform — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Merchant Lending Platform)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Merchant Lending Platform API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Merchant Lending Platform: regional failover',
                        'body': 'For Merchant Lending Platform, fence home epoch, replay outbox, '
                                'run recon, resume when breaks clear — domain-specific invariants '
                                'in section 3.'},
                       {'title': 'Merchant Lending Platform: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Merchant Lending Platform: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Merchant Lending Platform: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Merchant Lending Platform: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Merchant Lending Platform — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Merchant Lending Platform — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'merchant-ledger-system-design.md',
  'title': 'Merchant Ledger Service',
  'focus': 'Merchant balances · Payout gates · Reserves · Statements',
  'scope': 'Design merchant-visible ledger ~200 post/s backed by internal double-entry.',
  'goal': 'bound **merchant-facing ledger views**—balances, holds, statements, no direct post.',
  'functional_reqs': [('Visibility?', 'Available pending', 'Derived from internal'),
                      ('Writes?', 'Internal only', 'No merchant journal post'),
                      ('Payout gate?', 'Available-reserves', 'RYW balance'),
                      ('Statements?', 'Monthly export', 'Immutable PDF+data'),
                      ('Multi-currency?', 'Per currency view', 'Separate balances'),
                      ('Disputes?', 'Reserve holds', 'Reflect pending'),
                      ('API?', 'GET balance transactions', 'Read mostly'),
                      ('Idempotency?', 'On internal mirror', 'Sync jobs'),
                      ('Recon?', 'Mirror vs core ledger', 'Alert drift'),
                      ('Caching?', 'Short TTL+version', 'Never stale payout'),
                      ('Timezone?', 'Statement boundaries', 'Merchant local'),
                      ('Audit?', 'Merchant-visible history', 'Append only')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Merchant Ledger Service',
          'Admin recon/replay hooks for Merchant Ledger Service',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Merchant Ledger Service design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Visibility? → Available pending → durable write + audit',
                  'Writes? → Internal only → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Multi-currency? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Merchant Ledger Service)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Merchant Ledger Service — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Merchant Ledger Service)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Merchant Ledger Service API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Merchant Ledger Service: regional failover',
                        'body': 'For Merchant Ledger Service, fence home epoch, replay outbox, run '
                                'recon, resume when breaks clear — domain-specific invariants in '
                                'section 3.'},
                       {'title': 'Merchant Ledger Service: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Merchant Ledger Service: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Merchant Ledger Service: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Merchant Ledger Service: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Merchant Ledger Service — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Merchant Ledger Service — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'ledger-third-party-routing-system-design.md',
  'title': 'Consistent Ledger + Unreliable Third-Party Routing',
  'focus': 'Ledger SW · Outbox route · Inquiry · Saga',
  'scope': 'Design consistent ledger with unreliable external router ~500 post/s.',
  'goal': 'bound **strongly consistent ledger + unreliable external router**—local commit first, '
          'outbox route, inquiry, recon breaks.',
  'functional_reqs': [('Ledger?', 'Strong consistent local', 'Commit first'),
                      ('Router?', 'Unreliable HTTP', 'Async outbox'),
                      ('External key?', 'Stable per operation', 'Never per retry'),
                      ('Timeout?', 'Inquiry not blind retry', 'Classify'),
                      ('Recon?', 'Break queue', 'Ops tickets'),
                      ('Ordering?', 'Local serial per book', 'External best effort'),
                      ('Compensation?', 'Reverse journal', 'If external failed confirmed'),
                      ('Idempotency?', 'Both sides keys', 'Linked'),
                      ('Availability?', 'Ledger not blocked', 'Decouple'),
                      ('Multi-region?', 'SW ledger home', 'Router regional'),
                      ('Audit?', 'Route attempts log', 'Append'),
                      ('API?', 'Post journal inquiry', 'Admin recon')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Consistent Ledger + Unreliable Third-Party Routing',
          'Admin recon/replay hooks for Consistent Ledger + Unreliable Third-Party Routing',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Consistent Ledger + Unreliable '
                   'Third-Party Routing design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Post balanced journal locally → commit → outbox route attempt',
                  'External router 200 → mark route COMPLETE',
                  'Router timeout → inquiry → found → COMPLETE without re-post journal',
                  'Router fail confirmed → compensation journal via workflow',
                  'Duplicate route external key → partner returns original → idempotent success',
                  'Recon job finds mismatch → open break → ops ticket'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Consistent Ledger + Unreliable Third-Party Routing)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Consistent Ledger + Unreliable Third-Party Routing — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Consistent Ledger + Unreliable Third-Party Routing)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Consistent Ledger + Unreliable Third-Party Routing API → Directory → Home '
              'Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Never block ledger on router',
                        'body': 'Ledger TX completes in <20ms; router async via outbox.'},
                       {'title': 'Wrong guess fix ledger',
                        'body': 'Never mutate — compensating journal only.'}],
  'extra_appendix': '### 8.19 Consistent Ledger + Unreliable Third-Party Routing — rollout '
                    'checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Consistent Ledger + Unreliable Third-Party Routing — load test '
                    'profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'distributed-metrics-counter-system-design.md',
  'title': 'Distributed Metrics Counter',
  'focus': 'Sharded counters · Flush · Exact vs approximate',
  'scope': 'Design distributed counters ~1M inc/s exact for billing approximate for analytics.',
  'goal': 'bound **distributed counters**—sharding, flush windows, exact billing vs HLL analytics.',
  'functional_reqs': [('Modes?', 'Exact vs approximate', 'Billing exact'),
                      ('Increment?', 'Sharded atomic', 'Local agg'),
                      ('Flush?', 'Periodic durable', 'WAL before ack'),
                      ('Read?', 'Sum shards+local', 'Staleness bound'),
                      ('Hot key?', 'Split counter', 'Per shard subkeys'),
                      ('Idempotency?', 'Flush replay safe', 'Dedupe batch'),
                      ('Billing?', 'Must be exact', 'No CRDT money'),
                      ('Dashboard?', 'HLL OK', 'Error bound'),
                      ('Multi-region?', 'Single writer shard', 'Or CRDT analytics only'),
                      ('Backfill?', 'Replay log', 'Idempotent'),
                      ('API?', 'inc get flush', 'Internal'),
                      ('Alerts?', 'Drift vs source', 'Recon')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Distributed Metrics Counter',
          'Admin recon/replay hooks for Distributed Metrics Counter',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Distributed Metrics Counter '
                   'design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Modes? → Exact vs approximate → durable write + audit',
                  'Increment? → Sharded atomic → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Hot key? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Distributed Metrics Counter)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Distributed Metrics Counter — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Distributed Metrics Counter)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Distributed Metrics Counter API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Distributed Metrics Counter: regional failover',
                        'body': 'For Distributed Metrics Counter, fence home epoch, replay outbox, '
                                'run recon, resume when breaks clear — domain-specific invariants '
                                'in section 3.'},
                       {'title': 'Distributed Metrics Counter: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Distributed Metrics Counter: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Distributed Metrics Counter: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Distributed Metrics Counter: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Distributed Metrics Counter — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Distributed Metrics Counter — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'local-activity-counting-system-design.md',
  'title': 'Near-Real-Time Local Activity Counting',
  'focus': 'Geo windows · Edge agg · Late events',
  'scope': 'Design local activity counts ~100K events/s operational not money SoT.',
  'goal': 'bound **hyperlocal activity counting**—geo cells, sliding windows, late events.',
  'functional_reqs': [('Input?', 'Activity events', 'Stream ingest'),
                      ('Geo?', 'Cell hierarchy', 'City block'),
                      ('Window?', '1m 5m 1h sliding', 'Tumbling option'),
                      ('Accuracy?', 'Approx OK', 'Error bound stated'),
                      ('Late events?', 'Watermark buffer', 'Drop or adjust'),
                      ('Privacy?', 'Aggregate only', 'No raw PII buckets'),
                      ('Use?', 'Ops dashboards', 'Not payout decisions'),
                      ('Edge?', 'Pre-aggregate', 'Reduce central load'),
                      ('Query?', 'count by cell window', 'Low latency'),
                      ('Scale?', 'Shard by geo', 'Hot city isolate'),
                      ('Uniques?', 'HyperLogLog', 'Not exact global'),
                      ('Backfill?', 'Replay kafka', 'Idempotent windows')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Near-Real-Time Local Activity Counting',
          'Admin recon/replay hooks for Near-Real-Time Local Activity Counting',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Near-Real-Time Local Activity '
                   'Counting design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Input? → Activity events → durable write + audit',
                  'Geo? → Cell hierarchy → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Late events? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Near-Real-Time Local Activity Counting)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Near-Real-Time Local Activity Counting — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Near-Real-Time Local Activity Counting)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Near-Real-Time Local Activity Counting API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Near-Real-Time Local Activity Counting: regional failover',
                        'body': 'For Near-Real-Time Local Activity Counting, fence home epoch, '
                                'replay outbox, run recon, resume when breaks clear — '
                                'domain-specific invariants in section 3.'},
                       {'title': 'Near-Real-Time Local Activity Counting: idempotency under '
                                 'retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Near-Real-Time Local Activity Counting: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Near-Real-Time Local Activity Counting: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Near-Real-Time Local Activity Counting: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Near-Real-Time Local Activity Counting — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Near-Real-Time Local Activity Counting — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'incident-dispatch-marketplace-system-design.md',
  'title': 'Superhero / Incident Dispatch Marketplace',
  'focus': 'Geo match · SLA · Idempotent assign',
  'scope': 'Design incident dispatch marketplace ~500/s no double-assign.',
  'goal': 'bound **dispatch marketplace**—geo matching, offers, SLA escalation, idempotent '
          'assignment.',
  'functional_reqs': [('Supply?', 'Heroes on duty', 'Location heartbeat'),
                      ('Demand?', 'Incidents', 'Priority severity'),
                      ('Match?', 'Geo+skills', 'Rank score'),
                      ('Assign?', 'First accept wins', 'TX idempotent'),
                      ('SLA?', 'Escalation timers', 'Auto re-offer'),
                      ('Audit?', 'Who assigned when', 'Immutable'),
                      ('Cancel?', 'Incident resolved', 'Release hero'),
                      ('Fairness?', 'Round robin geo', 'Anti starvation'),
                      ('Pay?', 'Optional ledger hook', 'Idempotent bounty'),
                      ('Regional?', 'Geo shard', 'Partition outages'),
                      ('Offers?', 'Expire TTL', 'No ghost accept'),
                      ('Retry?', 'Same incident_id key', 'No double assign')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Superhero / Incident Dispatch Marketplace',
          'Admin recon/replay hooks for Superhero / Incident Dispatch Marketplace',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Superhero / Incident Dispatch '
                   'Marketplace design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Supply? → Heroes on duty → durable write + audit',
                  'Demand? → Incidents → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'SLA? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Superhero / Incident Dispatch Marketplace)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Superhero / Incident Dispatch Marketplace — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Superhero / Incident Dispatch Marketplace)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Superhero / Incident Dispatch Marketplace API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Superhero / Incident Dispatch Marketplace: regional failover',
                        'body': 'For Superhero / Incident Dispatch Marketplace, fence home epoch, '
                                'replay outbox, run recon, resume when breaks clear — '
                                'domain-specific invariants in section 3.'},
                       {'title': 'Superhero / Incident Dispatch Marketplace: idempotency under '
                                 'retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Superhero / Incident Dispatch Marketplace: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Superhero / Incident Dispatch Marketplace: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Superhero / Incident Dispatch Marketplace: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Superhero / Incident Dispatch Marketplace — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Superhero / Incident Dispatch Marketplace — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'recurring-payment-scheduling-system-design.md',
  'title': 'Recurring Payment Scheduling',
  'focus': 'Billing cycles · Dunning · Timezone · Idempotent charge',
  'scope': 'Design recurring billing ~1K bills/s peak idempotent per cycle.',
  'goal': 'bound **subscription billing scheduler**—cycles, dunning, timezone, idempotent charges.',
  'functional_reqs': [('Scheduler?', 'Durable timer queue', 'Not cron single box'),
                      ('Cycle key?', 'subscription+cycle_id', 'Idempotency'),
                      ('Timezone?', 'Merchant billing TZ', 'DST policy'),
                      ('Dunning?', 'Retry schedule', 'State machine'),
                      ('Cancel?', 'Stop future cycles', 'Race with charge TX'),
                      ('Proration?', 'Mid-cycle change', 'Ledger journals'),
                      ('Invoice?', 'Generate before charge', 'Immutable'),
                      ('Webhook?', 'invoice.paid failed', 'Outbox'),
                      ('Leap day?', 'Explicit rules', 'Feb 29 policy'),
                      ('Pause?', 'Skip cycles', 'Resume date'),
                      ('Ledger?', 'Charge journal', 'journal_key'),
                      ('Scale?', 'Shard by merchant', 'Peak midnight bursts')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Recurring Payment Scheduling',
          'Admin recon/replay hooks for Recurring Payment Scheduling',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Recurring Payment Scheduling '
                   'design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Scheduler? → Durable timer queue → durable write + audit',
                  'Cycle key? → subscription+cycle_id → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Cancel? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Recurring Payment Scheduling)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Recurring Payment Scheduling — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Recurring Payment Scheduling)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Recurring Payment Scheduling API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Recurring Payment Scheduling: regional failover',
                        'body': 'For Recurring Payment Scheduling, fence home epoch, replay '
                                'outbox, run recon, resume when breaks clear — domain-specific '
                                'invariants in section 3.'},
                       {'title': 'Recurring Payment Scheduling: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Recurring Payment Scheduling: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Recurring Payment Scheduling: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Recurring Payment Scheduling: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Recurring Payment Scheduling — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Recurring Payment Scheduling — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'idempotent-payment-processing-system-design.md',
  'title': 'Retry-Safe Idempotent Payment Processing',
  'focus': 'Idempotency deep dive · PROCESSING · Inquiry · Rail uncertain',
  'scope': 'Deep-dive idempotent payments ~1K QPS retry storms safe.',
  'goal': 'deep-dive **retry-safe idempotent payment processing**—idempotency store mechanics, '
          'PROCESSING, body hash, inquiry, ledger key coupling.',
  'functional_reqs': [('Key scope?', 'Per merchant endpoint', 'Global unique OK'),
                      ('Body hash?', 'SHA256 canonical JSON', '409 mismatch'),
                      ('PROCESSING?', 'Visible state', 'Sweeper resolves'),
                      ('Retention?', 'Years captures', 'Not 24h'),
                      ('Client guidance?', 'Same key retry', 'Never new key same event'),
                      ('Rail timeout?', 'Inquiry rail', 'Not blind retry'),
                      ('Response cache?', 'Store full HTTP', 'Replay identical'),
                      ('Ledger key?', 'Match payment key', 'Recon link'),
                      ('Partial?', 'Idempotent partial capture', 'Amount in hash'),
                      ('Webhooks?', 'After commit', 'Stable ids'),
                      ('Metrics?', '409 rate stuck age', 'Alert'),
                      ('Testing?', 'Chaos duplicate POST', 'Property tests')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Retry-Safe Idempotent Payment Processing',
          'Admin recon/replay hooks for Retry-Safe Idempotent Payment Processing',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Retry-Safe Idempotent Payment '
                   'Processing design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Key scope? → Per merchant endpoint → durable write + audit',
                  'Body hash? → SHA256 canonical JSON → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Client guidance? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Retry-Safe Idempotent Payment Processing)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Retry-Safe Idempotent Payment Processing — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Retry-Safe Idempotent Payment Processing)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Retry-Safe Idempotent Payment Processing API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Client uses new key after timeout',
                        'body': 'Explain double charge risk — coach same key retry; server stores '
                                'response cache.'},
                       {'title': 'Body hash canonicalization',
                        'body': 'JSON key sort; whitespace normalize; document for SDK authors.'}],
  'extra_appendix': '### 8.19 Retry-Safe Idempotent Payment Processing — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Retry-Safe Idempotent Payment Processing — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'async-financial-workflow-scheduling-system-design.md',
  'title': 'Async Financial Workflow Scheduling',
  'focus': 'Sagas · Timers · Compensation · Idempotent steps',
  'scope': 'Design financial workflows ~10K events/s payouts fees sweeps durable.',
  'goal': 'bound **async financial workflows**—state machines, timers, compensations, idempotent '
          'steps.',
  'functional_reqs': [('Workflow?', 'Durable state machine', 'Not in-memory'),
                      ('Steps?', 'Idempotent by step key', 'Attempt epoch'),
                      ('Timers?', 'At-least-once fire', 'Dedupe lease'),
                      ('Compensation?', 'Reverse prior steps', 'Idempotent undo'),
                      ('Human task?', 'Manual approve', 'Dual control'),
                      ('Ledger?', 'Step posts journal', 'Linked'),
                      ('Visibility?', 'Status query API', 'History append'),
                      ('Version?', 'Workflow definition ver', 'Migrate carefully'),
                      ('Pause?', 'Admin signal', 'Audit'),
                      ('Multi-region?', 'SW workflow home', 'Fence timers'),
                      ('Poison?', 'DLQ step', "Don't block"),
                      ('Batch payout?', 'Fan-out child workflows', 'Parent tracks')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Async Financial Workflow Scheduling',
          'Admin recon/replay hooks for Async Financial Workflow Scheduling',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Async Financial Workflow '
                   'Scheduling design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['Workflow? → Durable state machine → durable write + audit',
                  'Steps? → Idempotent by step key → correct domain behavior',
                  'Retry with same Idempotency-Key → stored response (no double effect)',
                  'Read-after-write from home cell → RYW consistent state',
                  'Human task? → safe degradation documented',
                  'Regional failover → epoch fence → outbox replay → recon before resume'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Async Financial Workflow Scheduling)\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Async Financial Workflow Scheduling — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Async Financial Workflow Scheduling)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Async Financial Workflow Scheduling API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Async Financial Workflow Scheduling: regional failover',
                        'body': 'For Async Financial Workflow Scheduling, fence home epoch, replay '
                                'outbox, run recon, resume when breaks clear — domain-specific '
                                'invariants in section 3.'},
                       {'title': 'Async Financial Workflow Scheduling: idempotency under retries',
                        'body': 'Same business key returns stored outcome; never second economic '
                                'effect; PROCESSING sweeper resolves ambiguity.'},
                       {'title': 'Async Financial Workflow Scheduling: 1000× scale knob',
                        'body': 'Shard by tenant/geo/resource id; isolate hot keys; never weaken '
                                'durability or idempotency for QPS.'},
                       {'title': 'Async Financial Workflow Scheduling: rollout',
                        'body': 'Dark launch shadow compare → cohort flag → authoritative cutover '
                                'with instant rollback.'},
                       {'title': 'Async Financial Workflow Scheduling: ops recon',
                        'body': 'Nightly compare internal aggregates vs external partners; open '
                                'breaks as tickets.'}],
  'extra_appendix': '### 8.19 Async Financial Workflow Scheduling — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Async Financial Workflow Scheduling — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'instagram-fallback-system-design.md',
  'title': 'Instagram-Like Feed (Stripe Fallback)',
  'focus': 'Fanout · Rank · Media · Idempotent post · Degrade',
  'scope': 'Design social feed ~500K read/s 10K post/s graceful degrade.',
  'goal': 'bound **Instagram-like feed** as Stripe fallback—post idempotency, fanout strategy, '
          'ranking degrade, not money SoT.',
  'functional_reqs': [('Post?', 'Idempotent publish_id', 'Never duplicate'),
                      ('Feed read?', 'Home timeline', 'Ranked'),
                      ('Fanout?', 'Hybrid celeb pull', 'Avoid write amp'),
                      ('Media?', 'CDN object store', 'Separate upload idem'),
                      ('Follow?', 'Graph edges', 'Consistent enough'),
                      ('Rank?', 'Precompute scores', 'Approx stale OK'),
                      ('Like?', 'Counter sharded', 'At-least-once inc'),
                      ('Delete?', 'Tombstone', 'Eventual remove'),
                      ('Celebrity?', 'Pull model', 'No sync fanout'),
                      ('Regional?', 'Read replicas', 'Post home cell'),
                      ('Degrade?', 'Chronological fallback', 'If ranker down'),
                      ('Consistency?', 'Eventual feed', 'Strong post ACK')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Instagram-Like Feed (Stripe Fallback)',
          'Admin recon/replay hooks for Instagram-Like Feed (Stripe Fallback)',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Instagram-Like Feed (Stripe '
                   'Fallback) design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['POST /posts with publish_id → durable post → 201',
                  'Celebrity post → pull model fans (no sync fanout)',
                  'Normal user post → hybrid fanout to active followers cache',
                  'GET /feed → merge followees → rank → return (stale OK 30s)',
                  'Ranker down → chronological fallback',
                  'Media upload idempotent object key → attach to post'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Instagram-Like Feed (Stripe Fallback))\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Instagram-Like Feed (Stripe Fallback) — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Instagram-Like Feed)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Instagram-Like Feed API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Celebrity fanout death',
                        'body': 'Pull model for >100K followers; precomputed celebrity feed '
                                'shard.'},
                       {'title': 'Feed consistency',
                        'body': 'Eventual OK — state strong post ACK only.'}],
  'extra_appendix': '### 8.19 Instagram-Like Feed (Stripe Fallback) — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Instagram-Like Feed (Stripe Fallback) — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'},
 {'file': 'ticketmaster-fallback-system-design.md',
  'title': 'Ticketmaster-Like Ticketing (Stripe Fallback)',
  'focus': 'Seat holds · Inventory · Idempotent purchase · Queue',
  'scope': 'Design ticketing ~50K hold/s 5K purchase/s anti-oversell.',
  'goal': 'bound **Ticketmaster-like ticketing**—seat holds, anti-oversell, waiting room, '
          'idempotent purchase, payment tie-in.',
  'functional_reqs': [('Inventory?', 'Seat map shards', 'Linearizable sold'),
                      ('Hold?', 'TTL token', 'Expire release'),
                      ('Purchase?', 'checkout_key idempotent', 'One sold state'),
                      ('Oversell?', 'TX lock seat row', 'Reject double'),
                      ('Queue?', 'Virtual waiting room', 'Fair token'),
                      ('Payment?', 'After seat TX', 'Hold token link'),
                      ('Partial cart?', 'Multi-seat atomic', 'All or none'),
                      ('Refund?', 'Release inventory', 'Ledger optional'),
                      ('Hot event?', 'Shard by section', 'Not one row'),
                      ('Regional?', 'Home per event shard', 'SW'),
                      ('Scan?', 'Ticket barcode unique', 'Fraud check'),
                      ('Resale?', 'Transfer lock', 'Policy')],
  'constraints': ['Integer minor units for money.',
                  'Exactly-once effect via idempotency keys.',
                  'Typed stable API errors.',
                  'Regional failure: fence, replay, recon.'],
  'scale_forces': {'10x': 'Idempotency+outbox+replicas',
                   '100x': 'Directory+cells+hot isolation',
                   '1000x': 'Regional homes+partitions+archive'},
  'mvp': ['POST /v1/resources',
          'GET /v1/resources/{id}',
          'Domain audit trail for Ticketmaster-Like Ticketing (Stripe Fallback)',
          'Admin recon/replay hooks for Ticketmaster-Like Ticketing (Stripe Fallback)',
          'Integration with idempotency + outbox patterns'],
  'out_of_scope': ['Multi-master active-active writers on same strong-consistency shard',
                   'Exactly-once end-to-end without client idempotency cooperation',
                   'Replacing all Stripe production systems in one Ticketmaster-Like Ticketing '
                   '(Stripe Fallback) design',
                   'Ad-hoc arbitrary SQL on primary OLTP for analytics'],
  'nfr': [('Write / mutate latency', 'Sync where applicable', 'p50 < 20ms, p99 < 100ms in-region'),
          ('Read latency', 'Dashboard + API', 'p99 < 200ms; RYW for critical reads'),
          ('Durability', 'Accepted state changes', 'Quorum commit before ACK'),
          ('Availability', 'Domain-critical paths', '99.99% home cell; degrade reads first'),
          ('Idempotency retention', 'Money-adjacent if applicable', 'Years — not 24h-only'),
          ('Multi-region', 'Global edge', 'Single-writer home per shard + fencing'),
          ('Audit retention', 'Compliance', 'Hot months + cold forever'),
          ('Scale target', '1000× headroom', 'See progressive scale table')],
  'happy_paths': ['POST hold → seat row lock TX → hold token TTL 10m',
                  'Hold expires → sweeper releases inventory',
                  'POST purchase checkout_key → verify hold → mark SOLD → payment',
                  'Duplicate purchase key → 200 original order',
                  'Waiting room token → admit to checkout shard',
                  'Payment fails → release hold or extend policy'],
  'edge_cases': [('Dup key same body', '200'),
                 ('Dup key diff body', '409'),
                 ('Timeout after commit', 'Idempotent retry'),
                 ('Hot shard', 'Isolate'),
                 ('Regional fail', 'Fence+replay'),
                 ('Duplicate idempotency key, same body', '200 + stored response'),
                 ('Duplicate key, different body', '409 idempotency_error'),
                 ('Write timeout after commit', 'Client retry → idempotent return'),
                 ('Stuck PROCESSING idempotency', 'Sweeper + upstream inquiry'),
                 ('Hot tenant / shard', 'Isolate cell; serialize or sub-shard'),
                 ('Regional partition', 'Home authority; edge fail-closed for critical writes'),
                 ('Outbox worker lag',
                  'Scale workers; alert; no duplicate apply if consumer idempotent'),
                 ('Cache stale on critical read', 'Bypass or version check against home SoT')],
  'scale_rows': [('Peak write QPS', '100', '1K', '10K', '100K'),
                 ('Peak read QPS', '1K', '10K', '100K', '1M'),
                 ('Tenants', '10K', '100K', '1M', '10M')],
  'estimation': {'traffic': 'See scale table',
                 'storage': '~1KB/row tiered',
                 'bandwidth': 'Regional cells at 1000x',
                 'memory': 'Sharded hot sets',
                 'bottlenecks': 'Idempotency, hot keys, outbox',
                 'extra': 'Split read/write QPS'},
  'entities': 'Resource, IdempotencyRecord, AuditEnvelope, OutboxEvent',
  'invariant': 'Accept implies durable commit before ACK; idempotent keys prevent double effect',
  'deal_breakers': [('ACK before durable', 'Ghost state'),
                    ('Skip idempotency', 'Double effect'),
                    ('Multi-master shard', 'Split brain')],
  'apis': ['POST /v1/resources', 'GET /v1/resources/{id}'],
  'protocols': 'Auth validate TX idempotency domain write outbox commit ACK',
  'hld_sections': '### 3.11 Domain model (Ticketmaster-Like Ticketing (Stripe Fallback))\n'
                  '\n'
                  'Core entities in section 3.1 compose the write path: validate invariants in TX, '
                  'append audit, emit outbox.\n'
                  '\n'
                  '### 3.12 Idempotency integration\n'
                  '\n'
                  'All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects '
                  'client bugs (409 conflict).\n'
                  '\n'
                  '### 3.13 Async boundary\n'
                  '\n'
                  'External systems (rails, routers, webhooks, third parties) invoked **after** '
                  'local durable commit via outbox workers with stable external keys.\n'
                  '\n'
                  '### 3.14 Ticketmaster-Like Ticketing (Stripe Fallback) — regional home\n'
                  '\n'
                  'Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie '
                  'writers fenced.',
  'diagrams': '### 4.1 End-to-end (Ticketmaster-Like Ticketing)\n'
              '\n'
              '```text\n'
              'Clients / Services → API Gateway (auth, rate limit)\n'
              '        → Ticketmaster-Like Ticketing API → Directory → Home Cell\n'
              '              (domain store + idempotency + audit + outbox)\n'
              '        → Async workers → External deps / Ledger / Webhooks\n'
              '        → Observability (metrics, traces)\n'
              '```\n'
              '\n'
              '### 4.2 Idempotent write sequence\n'
              '\n'
              'POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → '
              'identical response.\n'
              '\n'
              '### 4.3 Uncertain external dependency\n'
              '\n'
              'Worker calls external API with stable idempotency key → timeout → inquiry (same '
              'key) → classify → complete or compensating action.\n'
              '\n'
              '### 4.4 Regional failover\n'
              '\n'
              'Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → '
              'resume traffic.\n'
              '\n'
              '### 4.5 Read path\n'
              '\n'
              'GET by id → route home → RYW from primary or version-checked cache; list queries '
              'may use replica with lag bound.',
  'deep_sections': [('5.10 Domain reliability', 'Invariants and outbox.'),
                    ('5.11 Domain scale', 'Shard and isolate hot keys.'),
                    ('5.12 Domain ops', 'Recon and runbooks.'),
                    ('5.13 Domain multi-region', 'Home cell fencing.'),
                    ('5.14 Domain cache', 'Version check money reads.'),
                    ('5.15 Domain rollout', 'Dark launch flags.')],
  'wrapup_decisions': [('Consistency', 'Single-writer home'),
                       ('Idempotency', 'Key+hash'),
                       ('Async', 'Outbox')],
  'wrapup_risks': ['Hot shard', 'Stuck PROCESSING', 'Failover bugs'],
  'interview_plan': [('0-5', 'Scope'),
                     ('5-15', 'API+entities'),
                     ('15-25', 'Idempotency'),
                     ('25-35', 'Multi-region'),
                     ('35-45', 'Scale')],
  'qa_pairs': [('Idempotency TTL?', 'Years for money.'),
               ('Fail open?', 'Closed for money paths.'),
               ('Float?', 'Never.'),
               ('Exactly-once?', 'Effect via keys.'),
               ('1000x?', 'Shard+partition.'),
               ('Ledger?', 'journal_key ties transition.'),
               ('Regional?', 'SW home.'),
               ('Recon?', 'First-class breaks.'),
               ('Dark launch?', 'Shadow compare.'),
               ('Integration round?', 'Coding not HLD.'),
               ('Hot tenant?', 'Isolate cell.'),
               ('Outbox?', 'Same TX.'),
               ('Cache money?', 'Version or bypass.'),
               ('PROCESSING?', 'Sweeper.'),
               ('Webhook?', 'Stable event_id.'),
               ('Pagination?', 'Cursor.'),
               ('Delete history?', 'Append-only.'),
               ('ABAC?', 'If auth topic.'),
               ('Rate limit?', 'Edge first.'),
               ('Trap float?', 'Minor units.')],
  'schema': 'resources(id,tenant_id,status,...); idempotency(...); outbox(...)',
  'api_sketch': 'POST /v1/resources → 201',
  'state_machine': 'created → active → terminal',
  'pseudocode': 'handle: upsertIdem→apply→outbox→complete',
  'glossary': [('Home cell', 'Single-writer shard region'),
               ('Outbox', 'Durable async queue in TX')],
  'related': 'ledger-bookkeeping, payment-processing',
  'interview_probes': [{'title': 'Double sell prevention',
                        'body': 'SELECT FOR UPDATE seat row or compare-and-swap sold bit in TX.'},
                       {'title': 'Payment before seat',
                        'body': 'Never — seat SOLD TX before payment capture charged.'}],
  'extra_appendix': '### 8.19 Ticketmaster-Like Ticketing (Stripe Fallback) — rollout checklist\n'
                    '\n'
                    '- [ ] Idempotency replay tests in CI  \n'
                    '- [ ] Failover runbook with epoch fencing  \n'
                    '- [ ] Recon job covers external dependencies  \n'
                    '- [ ] Feature-flag default safe on outage  \n'
                    '- [ ] Load test with 5% retry injection  \n'
                    '\n'
                    '### 8.20 Ticketmaster-Like Ticketing (Stripe Fallback) — load test profile\n'
                    '\n'
                    '```text\n'
                    'warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak\n'
                    'inject: 5% duplicate idempotency keys, 1 regional failover at t=30m\n'
                    'assert: zero duplicate domain effects, recon breaks < threshold\n'
                    '```\n'}]
