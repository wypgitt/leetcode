#!/usr/bin/env python3
"""Senior/staff system-design doc generators — Part 2 (5 topics).

Each `doc_*()` returns a complete markdown string (does not write files).
"""
from __future__ import annotations

from _gen_senior15 import header, s1, s2, s3, s4, s5, s6, s7, s8


def _qa(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    assert len(pairs) >= 22, f"need >=22 Q&As, got {len(pairs)}"
    return pairs


def _bullets(title: str, lines: list[str]) -> str:
    body = "\n".join(f"- {x}" for x in lines)
    return f"**{title}**\n\n{body}\n"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    sep = "|".join(["---"] * len(headers))
    head = "| " + " | ".join(headers) + " |"
    mid = "|" + sep + "|"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return f"{head}\n{mid}\n{body}\n"


# =============================================================================
# 1. Model / Inference Gateway
# =============================================================================

def doc_model_gateway() -> str:
    deep_routing = """Aliases decouple products from provider model IDs. A `ModelRoute` carries primary, ordered fallbacks, and optional weighted canary.

**Selection:** `hash(request_id)` → weighted candidate. Pin `route_snapshot_id` for the request lifetime.

**Fallback triggers:** connect errors, timeouts, 429/5xx (policy), TTFT SLO breach (optional hedge for non-stream). Never fallback on user 400s.

**Headers:** always emit `x-model-resolved`, `x-request-id`, `x-ratelimit-*` so clients and support can debug.

**Canary:** compare TTFT, 5xx, safety block rate, $/1K tokens; auto-rollback on burn. Silent quality regressions need product feedback loops (re-ask rate), not only infra metrics.

**Normalization:** map finish reasons, usage, tool-call shapes into a canonical schema across OpenAI/Anthropic/vLLM.

""" + _bullets("Operational rules", [
    "Canary starts at 1–5%; step only after error-budget check",
    "Dual-run shadow traffic for risky models (bill to eval budget)",
    "Provider ToS / residency must be encoded on ProviderRef",
    "Kill switches: alias, provider, tenant — scoped and audited",
])

    deep_stream = """SSE events carry token deltas; heartbeats every 15s keep proxies alive. Bounded buffers (~256KB); slow clients pause or cancel upstream — never unbounded queues.

**Timeouts:** connect, TTFT, inter-token idle, total wall. Typical interactive: TTFT 15s, idle 30s, total 10 min.

**Cancel:** propagate to SaaS/vLLM; release concurrency; emit partial usage with `status=canceled`. Finance prefers slight overcount with reconcile over silent undercount.

**Idempotency:** `Idempotency-Key` for non-stream completes (TTL 24h). Streams are not replayed as full SSE.

**Multimodal:** upload large images to object store; pass URL to provider to keep gateway RAM flat.

""" + _table(
        ["Knob", "Baseline", "Notes"],
        [
            ["TTFT timeout", "15s", "Separate cold-start budget for self-host"],
            ["Idle timeout", "30s", "Heartbeats don't reset if no tokens"],
            ["Max buffer", "256KB", "Cancel if exceeded"],
            ["Max concurrent / key", "50–200", "Class-dependent"],
        ],
    )

    deep_quota = """Dimensions: RPM, TPM, concurrent streams, max request tokens, daily USD, burst multipliers.

**Algorithms:** token bucket (RPM/TPM); atomic concurrency counter; minute/day spend buckets. Soft limit (throttle/warn) then hard block.

**Classes:** interactive vs batch vs eval. Batch uses leftover capacity; never starve interactive beyond SLO.

**Distribution:** cell-local meters with tenant pin at 100×+. Brief overage allowed then hard stop. Hot product keys are naturally sharded by key id — avoid global locks.

**Cost pre-admit:** approximate tokens with local tokenizer; reject obvious overflows before provider call.

""" + _bullets("Fairness knobs", [
    "Per-route concurrency separate from per-tenant",
    "Shed batch first under provider 429 storms",
    "Budget inheritance: org → team → key",
    "Emergency borrow credits with dual control",
])

    deep_cache = """Exact/prefix cache hashes stable system instructions + tools. Prefer provider-native cache; gateway may cache identical complete requests only when `temperature=0` and deterministic.

**Isolation:** cache keys include `tenant_id|model|prefix_hash` — never content-only.

**Metering:** `prompt_tokens`, `completion_tokens`, `cache_read_tokens`, `cache_write_tokens`, `estimated_usd`. Pipeline: local WAL → Kafka → OLAP (<1 min) → warehouse invoices.

**Disputes:** retain request_id↔usage 90 days; sample prompts only with explicit debug flag.

""" + _table(
        ["Field", "Purpose"],
        [
            ["cache_read_tokens", "Discounted billing"],
            ["cache_write_tokens", "First-fill cost"],
            ["provider_invoice_hint", "Reconcile vs SaaS bill"],
            ["fallback_from", "Attribute quality/cost shifts"],
        ],
    )

    deep_safety = """Tiered path: (1) regex/blocklist + size (µs–ms), (2) lightweight classifier (ms), (3) heavy async judge off TTFT path.

**Input:** scan user+tool messages; optional PII redaction. **Output:** rolling window every K tokens; on block, error event + cancel upstream.

**Tools:** schema validate; allow-list egress for browse; sandbox code tools out-of-band.

**Fail mode:** fail-closed for high-risk categories; fail-open configurable for low-risk with audit. False-positive break-glass with dual control.

""" + _bullets("Latency budget", [
    "Rules < 1ms p99",
    "Light classifier < 8ms p99 on CPU pool",
    "Never run second LLM judge inline on interactive TTFT path",
    "Stream scan pipelined with token forward",
])

    deep_multi = """Credentials in KMS; dual-credential rotation; short-lived tokens when possible. Egress allow-list provider endpoints — admin registry only (no user `base_url` → SSRF).

mTLS to self-hosted meshes; per-provider connection pools with max lifetime. Abuse: TPM spikes, image floods, credential stuffing → key quarantine APIs.

""" + _table(
        ["Threat", "Control"],
        [
            ["Key leak", "Rotate + quarantine + audit"],
            ["SSRF", "Admin-only endpoints + egress ACL"],
            ["Prompt exfil via logs", "Default no-store; sampled debug opt-in"],
            ["Cross-tenant cache", "Tenant in cache key + cell isolation"],
            ["Cost bomb", "Daily USD hard cap + anomaly detection"],
        ],
    )

    qs = _qa([
        ("Why not let each microservice call OpenAI directly?",
         "You lose unified quotas, cost attribution, fallback, safety, and canary control. The gateway is the spend and blast-radius control point."),
        ("SSE vs WebSockets for tokens?",
         "SSE fits server→client token streams, standard HTTP auth, and proxies. WebSockets help duplex mid-stream control; many clients cancel via AbortController + HTTP cancel instead."),
        ("How do you idempotently retry a chat completion?",
         "Non-stream: Idempotency-Key stores final response (TTL 24h). Stream: do not replay SSE; cancel first attempt before retry; document partial usage."),
        ("Where is the source of truth for budgets?",
         "Warehouse for invoices; online meter for admission. Reconcile daily and adjust meters when drift > tolerance (e.g. 2%)."),
        ("How do you prevent cross-tenant prompt cache leaks?",
         "Cache keys include tenant_id and model; never key only on content hash. High-assurance tenants get separate cells."),
        ("What headers should clients see?",
         "`x-request-id`, `x-model-resolved`, `x-ratelimit-*`, optional `x-cache`, `x-fallback`."),
        ("How to handle provider rate limits?",
         "Map to 429 + Retry-After; shed lowest priority; failover if sustained; never infinite retry loops."),
        ("Can you hedge requests?",
         "Optional for short non-stream embeds/completes after a delay; cancel loser; bill winner carefully. Avoid hedging long streams."),
        ("How is TTFT defined?",
         "Accept → first SSE token event. Traces break out auth, admit, provider wait, safety."),
        ("Model registry consistency model?",
         "Eventually consistent push (<5s) is OK; pin snapshot per request. Admin reads should be strong."),
        ("How to price cache hits?",
         "Track cache_read tokens separately; pass through provider pricing; expose in usage events and invoices."),
        ("Structured outputs at the gateway?",
         "Validate JSON schema; optionally constrained decoding on self-hosted; return clear 422 on mismatch."),
        ("GPU scheduling vs gateway?",
         "Gateway admits logical requests and routes; GPU scheduler packs accelerators. Do not conflate the two control planes."),
        ("Multi-region with data residency?",
         "Pin tenant to region; forbid cross-geo fallback unless approved; encode on ProviderRef."),
        ("Kill switch design?",
         "Scoped: alias disable, tenant quarantine, provider disable, global emergency — audited and reversible."),
        ("How to test adapters?",
         "Contract tests with fixtures; chaos: latency, partial SSE, connect reset, duplicate chunks."),
        ("Concurrency limit heuristic?",
         "concurrent ≈ target_QPS × avg_duration, plus headroom; separate batch caps."),
        ("Tool calls and metering?",
         "Count relayed tool tokens; external tool latency must not hold model concurrency forever — separate timeouts."),
        ("Semantic cache risks?",
         "Wrong answer reuse across different intents; start with exact/prefix only; semantic needs strict allow-lists."),
        ("Cost attribution on fallbacks?",
         "Bill the provider/model that produced tokens; tag `fallback_from` for quality analysis."),
        ("Streaming through proxies?",
         "Disable response buffering; tune idle timeouts; prefer HTTP/2; send SSE comments as heartbeats."),
        ("Embeddings at millions QPS?",
         "Separate pool, batching, locality; do not share chat stream workers with embedding flood traffic."),
        ("Control plane SLOs?",
         "Admin API 99.9%; route propagation p99 < 5s; canary rollback < 60s after burn detection."),
        ("Prevent SSRF via custom base_url?",
         "Disallow user-specified URLs; only admin registry; egress allow-list."),
        ("Build vs adopt open-source gateway?",
         "Adopt commodity adapters; build multi-tenant policy, metering, and isolation if that is your platform edge."),
    ])

    return (
        header(
            "Model / Inference Gateway (LLM API Gateway)",
            "Auth · Routing · Quotas · Streaming SSE · Retries · Model registry · Fallback · Batching · Prompt cache · Multi-provider · Cost metering · Safety hooks",
            "Unify LLM providers behind one gateway with token economics, stream reliability, and tenant isolation",
        )
        + s1(
            goal="**bound an LLM inference gateway**: one API for apps to call models with auth, routing, quotas, streaming, retries, cost control, and safety — without each product reinventing provider glue.",
            is_is_not=[
                ("Job", "Multi-tenant API gateway in front of LLM / multimodal inference", "Training cluster, fine-tune runner, or full RAG product"),
                ("Traffic", "Chat completions, embeddings, tool-calls, batch, streaming tokens", "General HTTP gateway for arbitrary microservices"),
                ("Routing", "Model alias → provider/model/version with fallback & canary", "DNS load balancer alone"),
                ("State", "Request ledger, usage meters, prompt-cache keys, safety decisions", "Long-term chat history (apps own that)"),
                ("Scale lens", "Concurrent streams + tokens/sec + cost/day", "GPU bin-packing (see GPU Scheduler)"),
                ("FAANG lens", "Quotas, blast radius, cost attribution, abuse", "Single SDK wrapper in one service"),
            ],
            functional=[
                ("Who calls?", "Internal services + partners via API keys / mTLS", "Service identity + scopes on hot path"),
                ("Sync vs stream?", "JSON complete + SSE token stream", "Stream is first-class"),
                ("Multi-provider?", "OpenAI-compatible, Anthropic, self-hosted vLLM, embeddings", "Adapters + normalized I/O"),
                ("Model aliases?", "Apps call `gpt-prod`; ops remap", "Registry with pins + rollout"),
                ("Quotas?", "Per tenant/key: RPM, TPM, streams, $/day", "Distributed limiter + budget meter"),
                ("Retries / fallback?", "Retry 429/5xx; fallback on SLO breach", "Retry policy + circuit + chain"),
                ("Batching?", "Optional for self-host / embedding batches", "Never break stream semantics"),
                ("Prompt caching?", "Provider cache + gateway prefix keys", "Hash stable prefixes; bill hits differently"),
                ("Safety?", "I/O filters, PII hooks, jailbreak scores", "Sync + async policy engines"),
                ("Cost metering?", "Tokens, cache hits, tool calls; invoice by tenant", "Usage bus + dashboards"),
                ("Tool calling?", "Pass-through + schema validation", "Validate JSON; size limits"),
                ("Embeddings & rerank?", "First-class routes", "Separate latency budgets"),
                ("Observability?", "Trace id, model, tokens, TTFT, TPS", "Logs + metrics + sample traces"),
                ("Admin?", "Register models, fallbacks, kill switches, canaries", "Control plane ≠ data plane"),
            ],
            mvp=[
                "Authn (API key + service JWT) and model allow-lists.",
                "OpenAI-compatible chat + embeddings with SSE streaming.",
                "Model registry: alias → provider endpoint + creds + limits.",
                "Per-key RPM/TPM and concurrent stream limits.",
                "Retry with jitter; fallback model chain + circuit breakers.",
                "Usage ledger: tokens, latency, cost estimate.",
                "Safety hooks: blocklist, max tokens, content filter.",
                "Admin API: upsert route, budget, emergency disable.",
                "Dashboards: TTFT p99, error rate, $/tenant, queue depth.",
                "Idempotency-Key for non-stream completes.",
            ],
            out_mvp=[
                "Global active-active sticky streams for all sessions",
                "Fine-tune job orchestration / dataset management",
                "End-user playground UI (gateway is infrastructure)",
                "Universal semantic prompt cache",
                "Training-time GPU scheduling (separate system)",
            ],
            nfr=[
                ("TTFT (stream)", "p50 < 400ms, p99 < 1.5s first token (warm)", "Split gateway vs provider"),
                ("Availability", "99.9% accept or clean 429/503", "Fallback; never hang"),
                ("Usage durability", "No silent lost billable events", "WAL + at-least-once bus"),
                ("Registry consistency", "Propagate < 5s", "Pin in-flight route snapshot"),
                ("Multi-region", "Regional data planes", "Sticky region; residency rules"),
                ("Security", "KMS secrets; no prompt log default", "Tenant isolation + audit"),
                ("Cost overhead", "Gateway < 5–10% of model $", "Avoid chatty control plane"),
                ("Abuse", "Hard caps + anomaly detection", "Flood / stuffing protection"),
            ],
            happy=[
                "Stream chat via `assistant-prod` → primary → SSE tokens → usage recorded.",
                "Embeddings batch 64 → provider → vectors → metered.",
                "Primary 503 → circuit → fallback within SLO.",
                "Tenant TPM hit → 429 Retry-After; others unaffected.",
                "Canary 5% new model → metrics → promote.",
                "Safety blocks mid-stream → error event + audit.",
            ],
            cases=[
                ("Client disconnect mid-SSE", "Cancel upstream; partial usage; release concurrency"),
                ("Provider stalls after TTFT", "Idle timeout; abort; retry/fallback if allowed"),
                ("Duplicate Idempotency-Key", "Return stored complete; no SSE replay"),
                ("Context overflow", "Reject 400 with estimate before provider when possible"),
                ("Key leak / abuse spike", "Kill switch; rotate; quarantine budget"),
                ("Bad registry endpoint", "Canary + auto-rollback on TTFT/error burn"),
                ("Budget clock skew", "Central meter; soft then hard limit"),
                ("Invalid tool JSON", "Validate; optional repair; else error"),
                ("Huge multimodal upload", "MIME/size gate; reject early"),
                ("Cache key collision risk", "Include model+tenant+hash"),
                ("Billing bus down", "Local WAL; continue; alert"),
                ("Partial unicode chunks", "Opaque framing; client reassembly"),
                ("Agent fan-out storm", "Concurrency caps; prioritize interactive"),
                ("Regional outage", "Failover pin override; residency limits documented"),
            ],
            scales=[
                ("Concurrent streams", "5K", "50K", "500K", "5M"),
                ("Chat req/min", "30K", "300K", "3M", "30M"),
                ("Tokens/sec (out)", "200K", "2M", "20M", "200M"),
                ("Tenants / API keys", "200 / 2K", "2K / 20K", "20K / 200K", "200K / 2M"),
                ("Embedding QPS", "2K", "20K", "200K", "2M"),
                ("Usage events/sec", "5K", "50K", "500K", "5M"),
                ("Models in registry", "50", "200", "1K", "5K"),
                ("Safety checks/sec", "10K", "100K", "1M", "10M"),
            ],
            jumps="""**10×:** Sharded quota service; separate stream/complete pools; fat provider conn pools.

**100×:** Regional cells; usage Kafka; prompt-cache tier; dedicated embedding clusters; tenant sticky cells.

**1,000×:** Edge terminate TLS; hierarchical budgets; capacity broker to GPU pools; global kill with blast-radius limits.""",
            constraints=[
                "Providers have opaque limits and changing tokenizers — estimate conservatively.",
                "Streaming is weakly idempotent — document semantics.",
                "Default no prompt retention for compliance.",
                "Normalize heterogeneous provider error codes.",
                "Bill the model that actually ran after retries/fallback.",
            ],
            scope="Design a multi-tenant **Model / Inference Gateway**: authenticate, route aliases, enforce RPM/TPM/concurrency/budgets, stream tokens, meter cost, apply safety, fail over — scaled by concurrent streams and tokens/sec.",
        )
        + s2(
            [
                ("Concurrent streams & memory",
                 """Baseline 5,000 concurrent SSE streams
In-flight state ~8 KB/stream → 40 MB (CPU/network dominate)
At 500K streams → 4 GB session state → sticky workers + load shed
Mean stream 20s → accepts/sec = 5000/20 = 250/s baseline
At 5M concurrent → 250K accepts/sec → edge fanout + many cells"""),
                ("Tokens/sec & bandwidth",
                 """200K tok/s out × ~4 chars ≈ 800 KB/s (~6.4 Mbps)
20M tok/s → ~640 Mbps aggregate; 200M → ~6.4 Gbps (cell shard)
Gateway overhead target < 20–40ms p99 (auth+quota+route)"""),
                ("Quota / TPM math",
                 """Tenant TPM 2,000,000; avg 2,000 tok/req → 1,000 RPM ≈ 16.7 QPS
Token bucket refill r = TPM/60
Concurrency cap prevents fan-out storms even with TPM remaining
Redis keys: tpm:{key}:{minute}, conc:{key} — no global lock"""),
                ("Cost metering volume",
                 """5K events/s × 400B ≈ 2 MB/s ≈ 170 GB/day raw
Kafka 3× ≈ 0.5 TB/day; 7d retain ~3.5 TB
Nightly reconcile vs provider invoices (±2%)
Cache hits billed 0.1–0.5× — track separately"""),
                ("Prompt cache savings",
                 """System prompt 3K tok; 40% calls share prefix
Without cache: 3K×0.4×30K RPM = 36M tok/min prefix
70% hit on that slice → save ~25M tok/min
Keys: hash(tenant|model|prefix); never cross-tenant"""),
                ("Retry amplification",
                 """Naive 3× retry → 3× load during outage
Retry only 408/429/502/503; max 2; jitter 50–400ms
Hedge only short non-stream; circuit open at 20% 5xx / 30s"""),
                ("Safety CPU",
                 """Classifier 5ms × 10K rps → ~50 cores
Cascade: rules filter ~90%; ML on remainder
Stream: scan every N tokens; don't buffer whole answer"""),
                ("Cell capacity example",
                 """Target cell: 50K streams, 2M tok/s, 20K RPM
200 streams/pod → 250 pods + 30% → ~325 pods
Quota: 100K ops/s; Redis 6 shards
Usage: 50K events/s; 12 Kafka partitions"""),
            ],
            bottleneck="""1) Provider capacity/limits → fallback + admission  
2) Stream fanout & TTFT → cells + pools  
3) Quota hotspots → sharded meters  
4) Usage lag → WAL + Kafka  
5) Safety compute → tiered filters""",
        )
        + s3(
            overview="Clients call a stable OpenAI-compatible API. The **data plane** authenticates, admits against quotas, resolves alias→route, applies safety, invokes a **provider adapter**, streams tokens, and emits **usage events**. A **control plane** owns registry, budgets, canaries, and kill switches. GPU packing is a sibling system; this gateway is policy + routing + metering.",
            components=[
                "Edge (TLS, WAF, size limits)",
                "Authn/Authz (keys, JWT, scopes)",
                "Admission & quota (RPM/TPM/concurrency/$)",
                "Model registry + router (weights, fallback, canary)",
                "Provider adapters (SaaS + vLLM)",
                "Streaming session manager (SSE, cancel, timeouts)",
                "Safety policy engine",
                "Prompt cache coordinator",
                "Usage collector → Kafka → billing",
                "Control plane admin + config distribution",
                "Observability (metrics, traces, audit, cost)",
                "Circuit breakers per route",
            ],
            apis="""POST /v1/chat/completions
  Authorization, Idempotency-Key?, X-Tenant-Request-Id
  { model, messages, stream, max_tokens, tools, temperature }
  → JSON or text/event-stream

POST /v1/embeddings  { model, input }
GET  /v1/models

Admin:
PUT /admin/models/{alias}
PUT /admin/budgets/{tenant}
POST /admin/kill/{alias}
POST /admin/canary/{alias}

Internal:
POST /internal/usage/replay
GET  /internal/routesnapshot""",
            data_model="""ModelRoute { alias, primary, fallbacks[], weights, caps, safety_profile, canary? }
ProviderRef { provider, model_id, base_url, secret_ref, timeout_ms, region }
ApiKey { key_id, tenant_id, hash, scopes[], model_allow[] }
Budget { tenant_id, daily_usd, tpm, rpm, max_concurrency }
UsageEvent { ts, tenant_id, key_id, alias, provider, model_id,
  prompt_tokens, completion_tokens, cache_hit_tokens, ttft_ms, status, request_id, usd }
SafetyDecision { request_id, stage, action, labels[], scores }
StreamSession { session_id, worker, route_snapshot_id, started, canceled? }""",
            tradeoffs=[
                ("API shape", "OpenAI-compatible", "Custom richer API", "Compatible + extensions via headers"),
                ("Quota store", "Redis buckets", "DB transactions", "Redis hot path; DB budget of record"),
                ("Routing", "Client picks provider", "Server alias", "Alias for ops control"),
                ("Streaming", "SSE", "gRPC bidi", "SSE externally; gRPC internal OK"),
                ("Cache", "Prefix/exact", "Semantic", "Prefix first"),
                ("Safety", "Inline block", "Async only", "Inline ship/block; async enrich"),
                ("Metering", "Sync billing DB", "Async events", "Async + WAL; nightly reconcile"),
            ],
            dealbreakers=[
                ("One shared key for all products", "No blast radius or cost attribution"),
                ("Blind stream replay retries", "Double cost + side effects"),
                ("Log all prompts by default", "Privacy/compliance landmine"),
                ("Single global Redis at 1,000×", "Melts; need cells"),
                ("No fallback/circuit breaker", "Single provider SEV = total outage"),
                ("Bill only on client ack", "Lost usage on disconnects"),
            ],
            why="Alias-based multi-provider gateway with hard admission and async metering matches how platform teams run LLM fleets: stable product APIs while ops remaps models, cost, and capacity.",
        )
        + s4(
            """flowchart LR
  Client -->|HTTPS SSE/JSON| Edge
  Edge --> Auth
  Auth --> Admit[Admit_Quota]
  Admit --> Router[Model_Router]
  Router --> SafetyIn[Safety_In]
  SafetyIn --> Adapter[Provider_Adapter]
  Adapter --> Prov[SaaS_or_vLLM]
  Adapter --> SafetyOut[Safety_Out]
  SafetyOut --> Client
  Adapter --> Usage[Usage_WAL_Kafka]
  Ctrl[Control_Plane] --> Router
  Ctrl --> Admit
  Registry[(Model_Registry)] --> Ctrl
  Usage --> Bill[(Billing_WH)]""",
            [
                ("Streaming chat sequence",
                 """Client -> Edge: POST /v1/chat/completions stream=true
Edge -> Auth: validate key + scopes
Auth -> Admit: RPM/TPM/concurrency/budget
Admit -> Router: resolve alias snapshot
Router -> SafetyIn: scan prompt
SafetyIn -> Adapter: start upstream
loop tokens
  Prov -> Adapter -> SafetyOut -> Client: SSE delta
Client disconnect/complete
Adapter -> Usage: UsageEvent
Admit: release concurrency"""),
                ("Fallback on provider failure",
                 """Adapter: 503 / stall timeout
Router: circuit++; pick fallback
Adapter -> Prov2: same request_id
alt ok: stream; usage provider=Prov2
else: 503 PROVIDER_UNAVAILABLE; usage failed"""),
                ("Canary promotion",
                 """Ctrl: canary 5% on alias
Router: hash(request_id) bucket
Metrics: TTFT, 5xx, block, $/1K
Auto-rollback or raise % → primary swap"""),
            ],
        )
        + s5(
            reliability=[
                "Idempotency-Key for non-stream completes (TTL 24h).",
                "Retry only retryable errors; honor Retry-After; jitter.",
                "Circuit breaker + outlier ejection per ProviderRef.",
                "Cancel upstream on client disconnect.",
                "Usage WAL before complete ack; at-least-once Kafka.",
                "Route snapshot pinned for request lifetime.",
                "Budget soft then hard; central meter.",
                "Safety fail-closed for high-risk; audited fail-open for low-risk.",
                "Dual credentials for secret rotation.",
                "Load shed: reject new streams before collapsing TTFT for all.",
            ],
            scalability=[
                ("Baseline", "1 region; gateway + Redis quotas + Kafka"),
                ("10×", "Stateless replicas; sharded Redis; embedding pool"),
                ("100×", "Regional cells; sticky tenants; cache tier"),
                ("1,000×", "Edge PoPs; hierarchical quotas; capacity broker"),
            ],
            maintainability=[
                "Adapter interface + contract tests.",
                "Registry changes via admin/PR with canary + audit.",
                "Flags for safety models and cache policies.",
                "Golden traffic replay in staging.",
                "SLO dashboards per alias and tenant.",
                "Runbooks: provider outage, budget runaway, key leak, bad canary.",
                "UsageEvent schema forward-compatible.",
                "Cell ownership; no SSH config in prod.",
            ],
            deep_dives=[
                ("Routing, fallback, and canaries", deep_routing),
                ("Streaming semantics & backpressure", deep_stream),
                ("Quotas, budgets, and fair admission", deep_quota),
                ("Prompt caching & cost metering", deep_cache),
                ("Safety hooks without killing latency", deep_safety),
                ("Multi-provider auth & secret hygiene", deep_multi),
            ],
        )
        + s6(
            designed="A cell-friendly **Model / Inference Gateway** with alias routing, hard admission, SSE cancel semantics, provider fallback/canaries, tiered safety, prompt-cache hooks, and at-least-once usage metering.",
            decisions=[
                "OpenAI-compatible API + server-side aliases.",
                "Async usage WAL/Kafka vs sync billing DB.",
                "Pin route snapshot; weighted canaries.",
                "Tiered safety to protect TTFT.",
                "Cells at 100×+ for blast radius.",
            ],
            risks=[
                "Tokenizer drift → bad pre-admit estimates.",
                "Silent canary quality regressions.",
                "Usage lag → budget overshoot.",
                "Residency mismatch on fallback.",
                "Cancel gaps → orphan generation spend.",
            ],
            plan=[
                ("0–5", "Requirements: stream, quotas, multi-provider, safety, cost"),
                ("5–12", "API + components; alias registry"),
                ("12–20", "BOTE: streams, tok/s, quota, usage"),
                ("20–32", "Deep: streaming, fallback, quotas"),
                ("32–40", "Safety + metering + scale jumps"),
                ("40–45", "Risks, SLOs, closer"),
            ],
            closer="If aliases, admission control, stream cancel, and usage integrity are right, products can move models weekly without rewrites — and finance can sleep.",
        )
        + s7(qs)
        + s8(
            [
                ("SLO cheat sheet",
                 _table(["SLO", "Target"], [
                     ["Gateway admit p99", "< 40ms"],
                     ["TTFT p99 (warm)", "< 1.5s"],
                     ["Cancel propagation", "< 1s"],
                     ["Usage eventually durable", ">= 99.99%"],
                     ["Wrong-tenant cache", "0"],
                     ["Canary auto-rollback", "< 60s after burn"],
                 ])),
                ("Ownership",
                 _table(["Area", "Owner"], [
                     ["Data plane", "Inference Platform"],
                     ["Registry / canary", "Inference Platform + Model Ops"],
                     ["Budgets / billing", "Platform FinOps"],
                     ["Safety policies", "Trust & Safety ML"],
                     ["Provider contracts", "Cloud Partnerships"],
                 ])),
                ("Failure drills",
                 """1. Primary provider 100% 503 for 15m — fallback absorbs.  
2. Kafka down 30m — WAL backs up; admit continues.  
3. Bad canary toxicity — auto-rollback.  
4. Quota Redis shard loss — local limits + shed.  
5. Key leak simulation — rotate + quarantine."""),
                ("Capacity worksheet",
                 """Streams_target = ____
Tok_out/s = ____
RPM = ____
TPM = ____
Pods ~= Streams_target / streams_per_pod
Redis QPS ~= 3–5 × admit_QPS
Kafka MB/s ~= events/s × 0.4KB"""),
                ("Error taxonomy",
                 _table(["Code", "Meaning", "Client action"], [
                     ["400", "Validation / context overflow", "Fix request"],
                     ["401/403", "Authz", "Rotate key / scopes"],
                     ["429", "Rate / budget", "Backoff Retry-After"],
                     ["503", "Provider unavailable", "Retry / degrade UX"],
                     ["504", "Upstream timeout", "Retry non-stream; new stream id"],
                 ])),
            ],
            [
                "Locked MVP: aliases, stream, quotas, fallback, usage, safety",
                "TTFT and cancel semantics defined",
                "Scale jumps to cells at 100×+",
                "Deal-breakers called out",
                "22+ deep Q&As",
                "FinOps reconcile path clear",
            ],
        )
    )


if __name__ == "__main__":
    # partial self-check for first doc while file is still being completed
    for name, fn in [("model-gateway", doc_model_gateway)]:
        c = fn()
        print(name, c.count("\n") + 1)
