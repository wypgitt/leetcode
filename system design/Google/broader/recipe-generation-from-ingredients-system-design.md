# System Design: Recipe Generation from Available Ingredients

> **Focus areas:** Inverted index ingredients→recipes · Coverage ranking · Substitutions · Optional LLM hybrid · Catalog scale · Freshness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct retrieval math, split lexical index vs generative fluff, explicit cold-start/catalog ops, deal-breakers for “LLM generates every recipe from scratch at QPS”  
> **Interview theme:** Google L5+ retrieval + ranking — inverted index, posting lists, substitutions graph, hybrid RAG optional, progressive catalog/query scale

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

Goal: **bound the product**—a service that, given a user’s **available ingredients** (and constraints), returns **ranked recipes** they can cook—via **inverted index retrieval**, **coverage/substitution-aware ranking**, and optionally an **LLM hybrid** for explanations or novel suggestions. This is not a full grocery marketplace checkout.

### 1.0 What this is / is not

| Dimension | **Recipe-from-ingredients (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Retrieve/rank recipes for pantry set | Instacart / delivery logistics |
| Success | High precision “cookable now”; useful near-misses | Michelin creativity as sole SoT |
| Data plane | Catalog index + query ranker | User social graph MVP |
| Query | Ingredients → ranked recipes | Arbitrary nutrition OLAP |
| Correctness | Ingredient IDs + structured recipes | Free-text LLM-only pantry parsing without grounding |

**Scope statement:** Design ingredient→recipe retrieval with inverted index, ranking (coverage, popularity, constraints), substitutions, optional LLM hybrid, and catalog scale through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Input? | List of ingredient IDs/names + optional qty | Normalize to canonical IDs |
| F2 | Output? | Ranked recipes with missing/used ingredients | Explainability required |
| F3 | Exact cookable only? | Prefer cookable; also “missing 1–2” | Soft coverage score |
| F4 | Substitutions? | Yes — yogurt↔sour cream etc. | Sub graph / ontology |
| F5 | Constraints? | Diet, allergens, time, cuisine, equipment | Filters + hard excludes |
| F6 | Quantities? | Phase 1.5 — scale servings | Qty-aware coverage later |
| F7 | Catalog size? | Millions of recipes at scale | Sharded inverted index |
| F8 | User pantry persist? | Yes | Pantry service |
| F9 | LLM? | Optional hybrid — not sole retrieval | RAG / rewrite / explain |
| F10 | Personalization? | Light — cuisine prefs, history | Rerank features |
| F11 | Multilingual? | Normalize synonyms | Ontology / alias table |
| F12 | UGC recipes? | Yes with quality score | Spam/quality pipeline |

**MVP functional scope:**

1. Canonical **ingredient ontology** (aliases → ID).  
2. **Inverted index**: ingredient → posting list of recipe IDs.  
3. Query: pantry set → candidate recipes via postings intersection/union.  
4. **Rank** by coverage, missing count, popularity, time, diet fit.  
5. **Substitution-aware** soft matches with penalty.  
6. Filters: allergens (hard), max time, cuisine.  
7. Optional LLM: explain “why”, suggest creative twist **grounded** in retrieved recipes.  
8. Pantry CRUD + “what can I cook tonight” API.

**Out of MVP:**

- Full grocery pricing / substitution at store SKU  
- Computer vision fridge photos as sole input (mention hook)  
- Autopilot meal-plan calendar optimization (Phase 2)  
- LLM generating ungrounded ingredient lists as catalog SoT  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Query latency | Interactive | p99 < 200–300ms (excl. slow LLM) |
| N2 | Availability | High read | 99.9% index replicas |
| N3 | Index freshness | New recipes | Minutes–hour OK MVP |
| N4 | Allergen safety | Critical | Hard filters; fail closed |
| N5 | Scale | Large catalog | 10M–100M+ recipes path |
| N6 | Explainability | Why ranked | Missing/used/subs in response |
| N7 | Cost | LLM optional/expensive | Lexical path default |
| N8 | Multitenancy | App + partners | Catalog namespaces |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User pantry `[chicken, rice, onion, garlic]` → ranked stir-fry / burrito bowls.  
2. Missing 1 ingredient → show with “add cumin”.  
3. Allergen `peanut` → never return peanut recipes.  
4. Sub: no buttermilk → mark recipes using milk+acid sub.  
5. LLM explain: “You have 90% of Butter Chicken—missing garam masala (sub: curry powder).”

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Empty pantry | Popular quick recipes / onboarding |
| Unknown ingredient string | Fuzzy match ontology; ask confirm |
| Pantry huge (200 items) | Cap posting merge; prefer rare ingredients first |
| Recipe with 30 ingredients | Coverage fraction + missing absolute |
| Conflicting diet tags | Fail closed on allergens |
| Index lag after recipe edit | Versioned docs; eventual consistent OK |
| LLM hallucination of ingredients | Ground in retrieved recipe IDs only |
| Synonym duplication (`scallion`/`green onion`) | Alias to one ID |
| Regional names | Locale-aware aliases |
| Spam UGC | Quality score gate before index |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Recipes | 100K | 1M | 10M | 100M |
| Canonical ingredients | 5K | 15K | 50K | 100K+ |
| Avg ingredients/recipe | 10 | 10 | 10–12 | 12 |
| Posting list entries | 1M | 10M | 100M+ | 1B+ |
| Query QPS | 1K | 10K | 100K | 1M |
| Pantry updates/s | 200 | 2K | 20K | 200K |
| LLM attach rate | 5% | 5–10% | selective | edge rewrite only |
| Index shards | 4 | 16 | 64–128 | 500+ |
| Regions | 1 | 3 | 8 | global |

**What each jump forces:**

- **10×:** Proper inverted index (not SQL `LIKE`); caching; ontology service.  
- **100×:** Sharded postings; WAND/DAAT early termination; sub-graph service; async index pipeline.  
- **1,000×:** Tiered postings (hot ingredients), geo catalogs, embedding retrieval optional, LLM strictly off critical path.

### 1.5 Etc. (Constraints & Assumptions)

- Recipes are **structured**: id, title, ingredient_ids[], optional qty, tags, steps, time, popularity.  
- Users tolerate “buy 1–2 more” suggestions.  
- Nutrition optional Phase 1.5.  
- Vision fridge parsing is an input adapter, not the core index.

**Scope statement to repeat back:**

> Design a recipes-from-pantry system using a canonical ingredient ontology, inverted index retrieval, coverage/substitution-aware ranking, hard allergen filters, and an optional grounded LLM layer—scaling the catalog and QPS through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Search queries** | Pantry → recipes | 1K QPS | 10K | Query tier |
| **Pantry writes** | Update ingredients | 200/s | 2K | Pantry DB |
| **Index updates** | Recipe CRUD | 10/s | 100/s | Index pipeline |
| **Ontology lookups** | Alias normalize | 2K/s | 20K | Memory cache |
| **LLM calls** | Explain / rewrite | 50/s | 500/s | Separate pool |
| **Image/CDN** | Recipe photos | high | higher | CDN |

**Anti-pattern:** mixing LLM token/s with inverted-index QPS in one budget.

### 2.2 Index size

```text
Baseline: 100K recipes × 10 ingredients = 1M postings
Posting entry ~8–16B (recipe_id + payload bits) → ~10–16 MB (+ inverted overhead)
1M recipes → ~100–200 MB postings — still small
100M recipes × 12 × 16B = ~19 GB postings raw → shard + compress (FOR/delta)
Doc store (title, steps): 100M × 5KB = 500 TB? too fat
  → keep thin doc in search; cold steps in blob/SQL; or 2KB truncated = 200 TB still huge
  → Practical: 100M is ambitious; store steps in object store; index holds ids+stats
```

### 2.3 Query cost (DAAT)

```text
Pantry size P = 15 ingredients
Naïve: intersect all posting lists — but we want recipes covering MANY not ALL
Better: UNION candidates from postings, score coverage

Candidate generation:
  Use rarest ingredients' postings first (IDF-like)
  Or: retrieve recipes that match ≥ T ingredients

Suppose each ingredient df average = (recipes * 10 / ingredients) 
  1M recipes, 15K ingredients → avg df ≈ 1M*10/15K ≈ 667
  Hot: salt/oil df ≈ 0.8 * recipes — MUST skip or demote as candidates alone

Strategy: sort pantry by ascending df; take top R rarest; union their postings; score all pantry
```

### 2.4 Latency budget

```text
Normalize ingredients: 5ms
Candidate gen: 20–50ms
Feature fetch / rank: 20–40ms
Assemble response: 10ms
Total lexical: < 150ms p99 target
LLM explain async or +1–3s optional path
```

### 2.5 Substitution fanout

```text
If each missing ingredient expands to S=5 subs, combinatorial explosion
Cap: only expand missing side with top-S subs; penalty in score
Never expand salt→everything
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/recipes/suggest` | Body: `{ingredients[], exclude_allergens[], diet[], max_time, max_missing, locale}` |
| `GET /v1/recipes/{id}` | Full recipe |
| `PUT /v1/users/{id}/pantry` | Replace/patch pantry |
| `GET /v1/users/{id}/pantry` | Current pantry |
| `GET /v1/ingredients/suggest?q=` | Typeahead ontology |
| `POST /v1/recipes/suggest:explain` | Optional LLM explanation for recipe set |
| `POST /internal/index/recipes` | Upsert recipe doc |

**Suggest response:**

```text
{
  results: [{
    recipe_id, title, score,
    used: [ing...],
    missing: [ing...],
    substitutions: [{needed, instead_use, confidence}],
    time_minutes, cuisine, tags
  }],
  next_cursor
}
```

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| Ingredient | `ing_id` | name, aliases, family, allergens, density |
| Recipe | `recipe_id` | title, ing_ids[], qty?, steps_ref, time, tags, popularity, quality |
| Posting | `ing_id` → list | `(recipe_id, tf, is_essential?)` sorted |
| Substitution | `(ing_a, ing_b)` | directed/undirected weight, context |
| Pantry | `user_id` | set/list of ing_ids (+ qty Phase 1.5) |
| User prefs | `user_id` | diets, cuisines, dislikes |
| Doc version | `recipe_id` | `ver` for index sync |

### 3.3 Retrieval model — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **SQL `WHERE ing IN` joins** | Simple | Dies at catalog scale | <10K recipes |
| **Inverted index union + score** | Proven IR | Need posting infra | **MVP+** |
| **Embeddings only** | Semantic | Weak exact coverage; allergen risk | Assistive rerank |
| **LLM generates recipes** | Creative | Hallucinations; cost; safety | Optional garnish |
| **Boolean MUST all ingredients** | Precise cookable | Empty results often | Mode toggle |

**Chosen MVP:** inverted index candidate gen → feature ranker → optional LLM explain.

### 3.4 Scoring model

```text
coverage = |pantry ∩ recipe_ings| / |recipe_ings|
missing = |recipe_ings - pantry|
soft_missing = missing after applying best subs
essential_penalty = count missing essentials

score =
  w1 * coverage
+ w2 * 1/(1+soft_missing)
+ w3 * popularity_norm
+ w4 * time_fit
+ w5 * pref_fit
- w6 * essential_penalty
- w7 * sub_penalty

Hard reject if allergen ∩ recipe_allergens ≠ ∅
```

**Deal-breaker:** ranking only by popularity ignoring coverage (“everyone gets chocolate cake”).

### 3.5 Candidate generation

```text
1. Map strings → ing_ids (ontology)
2. Drop ultra-common pantry items from driving terms (salt, water, oil) OR down-weight
3. Sort remaining by ascending df (rarest first)
4. Union postings of first R rarest until candidate set ≥ M or terms exhausted
5. Optionally add recipes from substitute ids with lower priority
6. Attach recipe thin docs; score; filter; return top K
```

**Why rare-first:** salt’s posting list is huge; chicken thighs’ list is selective.

### 3.6 Substitutions — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Static pair table** | Simple editable | Sparse | **MVP** |
| **Ingredient taxonomy / embedding** | Coverage | False friends (allergy!) | Assisted |
| **LLM suggest sub** | Flexible | Unsafe alone | Needs ontology validate |
| **Culinary rules engine** | High quality | Expensive to build | Vertical depth |

**Safety:** never substitute across allergen boundaries (peanut ↔ almond still nut risk—policy matrix).

### 3.7 LLM hybrid

```text
Path A (default): lexical suggest — fast, safe
Path B: retrieve top K → LLM summarize / meal plan / rewrite steps
Path C: LLM parse messy text pantry → ontology linker → Path A

Never: LLM invent catalog recipe as allergen-safe without structured check
```

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Retrieval | Inverted index | Scale + exact IDs | SQL LIKE / LLM-only |
| Driving terms | Rare ingredients | Cut fanout | Drive from salt/oil |
| Subs | Table + penalty | Controllable | Silent unsafe subs |
| Allergens | Hard filter | Safety | Soft rank only |
| LLM | Optional grounded | Cost/safety | LLM as SoT catalog |
| Index | Near-real-time pipeline | Fresh UGC | Weekly batch only at 100× UGC |

---

## 4. Architecture Diagram

```text
  Apps -----------------+
                        v
                 +------+-------+
                 | API Gateway  |
                 +------+-------+
                        |
        +---------------+----------------+----------------+
        v               v                v                v
 +------+------+ +------+------+ +------+------+  +------+------+
 | Pantry Svc  | | Suggest Svc | | Ontology    |  | Recipe Read |
 | (user set)  | | (rank)      | | / aliases   |  | (docs)      |
 +------+------+ +------+------+ +------+------+  +------+------+
        |               |                ^                ^
        |               v                |                |
        |        +------+------+         |                |
        |        | Query Fanout|---------+                |
        |        | Index shards|                          |
        |        +------+------+                          |
        |               ^                                 |
        v               | postings                        |
 +------+------+        |                          +------+------+
 | User DB     |        |                          | Doc Store   |
 +-------------+        |                          | (SQL/BT)    |
                        |                          +------+------+
                 +------+------+                          ^
                 | Indexer     |<---- Kafka recipe events-+
                 | (build)     |      UGC / editorial
                 +------+------+
                        |
                        v
                 +------+------+     +---------------+
                 | Sub Graph   |     | LLM Service   |
                 | (pairs)     |     | (optional)    |
                 +-------------+     +---------------+

 Cache: popular pantry signatures → top-K (careful with PII)
 CDN: images
```

---

## 5. Design Deep Dive

### 5.1 Ontology & normalization

```text
"Green Onions" → nfkc/casefold → alias lookup → ing:scallion
"coriander leaves" (US cilantro) → locale map
Unknown → fuzzy (edit distance / n-gram) → top-3 confirm
```

**Maintainability:** editors manage aliases; automated mining from logs with human approve.

### 5.2 Posting list encoding

```text
ing_id → [recipe_id delta-encoded][payload: essential_bit, tf]
Skip pointers / blocks for DAAT
Hot ingredients: bitset or "too common" flag → never sole driver
```

### 5.3 Ranking features

| Feature | Source |
|---------|--------|
| coverage / missing | set math |
| sub_penalty | sub graph |
| popularity | clicks, makes, saves |
| quality | rating, spam model |
| time_fit | \|t - preferred\| |
| cuisine_pref | user prefs |
| novelty | not made recently |
| seasonality | optional |

**Two-stage:** cheap score on candidates → heavy rerank top 200 (incl. embeddings optional).

### 5.4 Allergen fail-closed

```text
recipe_allergens = union(ingredient.allergens)
if intersection(user_allergens, recipe_allergens): drop
if unknown allergen tagging on any essential ing: drop or demote per policy
```

**Deal-breaker:** “best effort” allergen matching without structured tags.

### 5.5 Index pipeline

```text
Recipe write → validate schema → Kafka
  → Indexer updates postings (add/remove ing deltas)
  → Doc store upsert
  → Version++
Near-real-time: seconds–minutes
Rebuild: weekly full MapReduce/Flink from source of truth
```

### 5.6 Query planning for large pantries

```text
if P > 40: cluster pantry by family; take top rare per family
Use minhash / posting sketches at 1,000× for first-cut
```

### 5.7 Caching

| Key | Value | TTL | Risk |
|-----|-------|-----|------|
| `sig = hash(sorted_ing_ids + filters)` | top-K ids | 5–30m | Privacy if URL-logged |
| ingredient typeahead | suggestions | long | Low |
| recipe doc | body | mid | Stale ok |

Prefer **anonymous signature cache** over raw user_id keys in shared CDN.

### 5.8 LLM hybrid details

| Use | Pattern |
|-----|---------|
| Parse messy list | LLM → JSON ingredients → ontology validate |
| Explain | Prompt with structured used/missing only |
| Creative | “variations” labeled non-authoritative |
| Steps simplify | Rewrite from stored steps |

**Cost control:** quota per user; batch; short prompts; cache explanations by `(recipe_id, pantry_sig)`.

### 5.9 Reliability

| Failure | Mitigation |
|---------|------------|
| Shard down | Replica; degrade partial candidates + flag |
| Ontology miss spike | Fallback fuzzy; metric alert |
| Bad deploy ranks allergens wrong | Canary; golden allergy test suite **blocker** |
| Kafka lag | Serve stale index; freshness SLO |
| LLM outage | Lexical-only degrade |

**Reliability principles:**

1. Allergen tests in CI.  
2. Index replicas ≥ 2.  
3. SoT recipes in DB; index derived.  
4. LLM never sole gate for safety.

### 5.10 Scalability

| Scale | Tactic |
|-------|--------|
| 10× | In-memory postings per shard; Redis pantry |
| 100× | Sharded index; WAND-style early exit; async indexer |
| 1,000× | Tiered postings, geo catalogs, embedding ANN assist, edge cache signatures |

**Sharding recipes:** by `recipe_id % N` — query fans out; merger ranks global top-K.

**Sharding postings:** by `ing_id` — query only touches pantry ingredients’ shards (better!).

**Chosen:** **shard by ingredient** for suggest QPS; doc store by recipe_id.

### 5.11 Maintainability

| Practice | Why |
|----------|-----|
| Ontology as data | Non-eng edits |
| Ranker config weights | Tunable without rewrite |
| Golden queries | Regression (“chicken+rice”) |
| Allergy fixtures | Safety |
| Separate LLM service | Blast radius |
| Versioned index schema | Rolling upgrades |

### 5.12 Quantity-aware Phase 1.5

```text
coverage_qty = sum min(have_q, need_q) / sum need_q
missing_qty for shopping list
Unit conversion via ontology densities — hard; keep optional
```

### 5.13 UGC quality

```text
spam model → quality score
index only quality ≥ threshold
report/takedown pipeline
```

### 5.14 Progressive scale

**Baseline:** 100K recipes, monolithic index service, Postgres recipes, Redis pantry.

**10×:** split ontology; posting lists in memory; suggest cache.

**100×:** ingredient-sharded index; Flink indexer; sub service; multi-region read.

**1,000×:** hot/cold postings; per-country catalog slices; ANN co-retrieval; LLM at edge for parse only.

---

## 6. Wrap-Up

### 6.1 Design summary

A **pantry→recipes** system grounded in a **canonical ingredient ontology** and **inverted index**, ranking by **coverage, substitutions, constraints, and popularity**, with **hard allergen filtering** and an **optional grounded LLM** for parse/explain—not for unsafe generation as SoT.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Lost |
|----------|--------|------|
| Exact vs semantic | Lexical first | Embedding-only recall |
| Cookable vs inspiring | Soft missing | Strict boolean only |
| LLM | Optional | Always-on gen cost |
| Shard axis | By ingredient | Fanout-all-recipe-shards |
| Subs | Explicit graph | Free-text creativity |

### 6.3 Deal-breakers

1. LLM-only catalog without structured ingredients.  
2. Soft-ranking allergens.  
3. Candidate gen driven only by salt/oil/water.  
4. SQL joins as sole plan at 10M recipes.  
5. Silent substitutions across allergen classes.  
6. Putting LLM on 100% QPS critical path.

### 6.4 Progressive scale one-liner

> **Ontology + inverted postings → rare-first candidates → sharded index & subs → tiered retrieval + grounded LLM off hot path.**

### 6.5 Reliability / Scalability / Maintainability

```text
Reliability: allergen fail-closed, derived index, degrade lexical-only
Scalability:  ingredient shards, rare-first, caches, geo catalogs
Maintainability: ontology data, golden queries, ranker weights, LLM isolated
```

---

## 7. Deeper / Related Interview Questions

### 7.1 Information retrieval

**Q1: Why inverted index?**  
A: Ingredient→recipes is classic term→doc; enables sparse retrieval at scale.

**Q2: Intersect vs union?**  
A: Intersection = uses all terms (often empty); union + coverage score fits pantry.

**Q3: How handle stop-ingredients?**  
A: Mark universal pantry items; exclude from driving terms.

**Q4: DAAT/WAND relevance?**  
A: Early termination when upper bound score can’t beat heap min.

**Q5: How compute IDF-like for ingredients?**  
A: `log(N/df)`; rare meats/spices dominate.

### 7.2 Ranking & product

**Q6: Missing-1 vs 90% coverage?**  
A: Blend absolute missing and fraction; small recipes shouldn’t dominate unfairly.

**Q7: Essential vs garnish ingredients?**  
A: Tag essentials; missing garnish lower penalty.

**Q8: Personalization without filter bubble?**  
A: Explore slot; diversity MMR.

**Q9: Shopping list mode?**  
A: Optimize minimize missing cost — Phase 2.

### 7.3 Substitutions & safety

**Q10: Is tofu a chicken sub?**  
A: Context/diet dependent; store typed edges with cuisine context.

**Q11: Allergen + sub?**  
A: Validate sub against user allergens before applying.

**Q12: Why not word2vec subs alone?**  
A: “Peanut” near “almond” geographically in embedding space—dangerous.

### 7.4 LLM

**Q13: Where LLM helps most?**  
A: Messy input parse, explanations, creative variations labeled soft.

**Q14: How prevent hallucination?**  
A: Constrained decode / tool use: only cite retrieved recipe_ids; verify ingredients ⊂ catalog.

**Q15: Latency?**  
A: Async explain endpoint; don’t block suggest.

### 7.5 Systems

**Q16: Shard by recipe or ingredient?**  
A: Ingredient shards minimize touched data for pantry queries.

**Q17: Freshness vs rebuild?**  
A: Incremental + periodic full rebuild for self-heal.

**Q18: Multi-region?**  
A: Replicate indexes; pantry home-region; catalog may be locale-specific.

**Q19: Cache stampedes on viral recipe?**  
A: Doc cache + singleflight; index immutable segments.

### 7.6 Estimation drills

**Q20: Postings bytes for 10M recipes × 10 ings × 8B?**  
A: 800 MB raw; with overhead ~2–4 GB—fits RAM sharded.

**Q21: QPS 100K with p99 200ms — threads?**  
A: Little’s Law: 100K × 0.2 = 20K concurrent requests—need async + many cores/shards.

### 7.7 Alternatives & deal-breakers

**Q22: Only embeddings ANN?**  
A: Weak for exact pantry coverage and allergens.

**Q23: Graph DB traversal?**  
A: Nice for subs; not a replacement for postings at catalog scale.

**Q24: Weekly batch index only?**  
A: Fails UGC freshness expectations.

### 7.8 Interview craft

**Q25: Opening?**  
A: Ontology, inverted index, coverage rank, allergens, optional LLM—scope out delivery.

**Q26: L5+ signals?**  
A: Rare-first driving terms, allergen fail-closed, shard-by-ing, LLM grounded, scale path.

**Q27: Common mistake?**  
A: Jumping to GPT generating recipes; ignoring index math and safety.

---

### Appendix A — Suggest pseudocode

```text
def suggest(pantry_raw, filters):
  ids = ontology.map(pantry_raw)
  drivers = drop_stop(ids).sort_by(df_asc)
  cands = empty_set()
  for t in drivers:
    cands |= postings[t]
    if len(cands) >= M: break
  cands |= sub_expand_cands(ids)  # capped
  scored = []
  for r in cands:
    if allergen_block(r, filters): continue
    scored.append((score(r, ids, filters), r))
  return top_k(scored, K)
```

### Appendix B — Score function

```text
def score(r, pantry, filters):
  used = r.ings & pantry
  missing = r.ings - pantry
  soft, sub_pen = apply_subs(missing, pantry)
  cov = len(used) / max(len(r.ings),1)
  return w1*cov + w2/(1+len(soft)) + w3*pop(r) - w6*ess_miss(r,soft) - w7*sub_pen
```

### Appendix C — Posting update

```text
onRecipeUpdate(old, new):
  for ing in old.ings - new.ings: postings[ing].remove(id)
  for ing in new.ings - old.ings: postings[ing].add(id)
  docs[id] = new
```

### Appendix D — Substitution edge

```json
{"from": "buttermilk", "to": "milk_plus_lemon", "weight": 0.8, "context": "baking"}
```

### Appendix E — Allergen matrix snippet

| Ingredient | Allergens |
|------------|-----------|
| peanut | PEANUT, TREE_NUT_POLICY? |
| milk | DAIRY |
| soy_sauce | SOY, WHEAT? |

### Appendix F — Progressive scale table

| Scale | Index | Query | LLM |
|-------|-------|-------|-----|
| Baseline | 1 node | Monolith | Off/rare |
| 10× | Multi replica | Cache sigs | Parse beta |
| 100× | Ing shards | WAND/heap | Explain async |
| 1,000× | Tiered+geo | Edge cache | Strict quota |

### Appendix G — API example

```json
POST /v1/recipes/suggest
{
  "ingredients": ["chicken thighs", "rice", "garlic", "soy sauce"],
  "exclude_allergens": ["peanut"],
  "max_missing": 2,
  "max_time": 45
}
```

### Appendix H — NFR card

```text
p99 suggest < 300ms lexical
Allergen fail-closed
Index freshness < 15m MVP
LLM optional non-blocking
```

### Appendix I — Embedding assist (Phase 2)

```text
Embed pantry bag / recipe → ANN top A
Union with lexical cands
Rerank — still apply allergen filters
```

### Appendix J — Pantry schema

```text
user_id → {ings: [{id, qty?, unit?, expiry?}]}
```

### Appendix K — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just use GPT” | Safety, cost, catalog grounding |
| “SQL is fine” | Until join fanout / df salt |
| “Subs are easy NLP” | Allergen false friends |
| “Cache everything” | Pantry privacy + combinatorics |

### Appendix L — Related systems

| System | Relation |
|--------|----------|
| Elasticsearch/Lucene/Vespa | Postings infra |
| Knowledge graph | Ontology/subs |
| Bigtable/SQL | Docs / pantry |
| LLM serving | Hybrid layer |
| Feature store | Ranker pops |

### Appendix M — Glossary

| Term | Meaning |
|------|---------|
| Posting list | Recipes containing an ingredient |
| Coverage | Fraction of recipe ings in pantry |
| Stop-ingredient | Ubiquitous pantry item |
| Grounding | LLM limited to retrieved facts |
| Essential | Ingredient critical to dish identity |

### Appendix N — Worked example

```text
Pantry: chicken, rice, onion, garlic, soy (dfs low→high except soy mid)
Drivers: chicken, soy, rice...
Union postings → 5K cands → score → top 20
Butter chicken missing cream+spices → soft_missing 3 → lower rank than stir-fry missing 0
```

### Appendix O — Consistency

| Question | Answer |
|----------|--------|
| Read-your-write recipe upload? | Wait for index version or sync path |
| Pantry strongly consistent? | Yes in home DB |
| Cross-region suggest same? | Eventual catalog |

### Appendix P — 30m checklist

1. Clarify cookable vs missing-k, allergens, LLM role.  
2. Ontology + inverted index.  
3. Rare-first candidates + score.  
4. Subs + fail-closed allergens.  
5. Estimate postings & QPS.  
6. Shard-by-ingredient.  
7. Scale jumps.  
8. Deal-breakers.

### Appendix Q — Quality signals

| Signal | Use |
|--------|-----|
| Saves / makes | Popularity |
| Bounce on recipe | Negative |
| “Made it” photos | Strong positive |
| Report spam | Quarantine |

### Appendix R — Multilingual

```text
locale → alias table → same ing_id
Recipe title localized in doc store
```

### Appendix S — Shopping list extension

```text
minimize cost(missing) s.t. meal plan constraints — ILP Phase 2
```

### Appendix T — Why not boolean MUST every pantry item appear?

```text
User has 40 items; recipes won't use all — wrong semantics
Query is "recipes ⊆ pantry (approx)" not "recipes ⊇ pantry"
```

### Appendix U — Index segment layout

```text
Segment: immutable postings + thin docs
Searcher: multi-segment merge heap
Refresh: reopen with new segment
```

### Appendix V — Golden allergy tests

```text
assert never_returns(pantry, allergens=["peanut"], recipe_with_peanut)
CI gated
```

### Appendix W — Ranker weight config

```text
w1=0.45 coverage
w2=0.25 missing
w3=0.15 pop
w4=0.10 time
w7=0.05 sub
```

### Appendix X — Typeahead

```text
Edge n-gram / prefix index on ingredient names → ids
```

### Appendix Y — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Real inverted index, ontology svc |
| 100× | Shards, indexer pipeline, sub svc |
| 1,000× | Tiered postings, geo, ANN assist |

### Appendix Z — Opening script

> “I'll retrieve cookable recipes with an ingredient ontology and inverted index, rank by coverage and substitutions, hard-filter allergens, and keep LLMs optional and grounded. We'll scale by sharding postings on ingredients and rare-first candidate generation.”

---

*End of Recipe Generation from Available Ingredients system design.*
