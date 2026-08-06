"""CIDR firewall matcher LLD topic."""

from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices

register("cidr-firewall-matcher-lld-system-design.md", lambda: build_doc([
    header(
        "IPv4 CIDR Firewall Rule Matcher",
        "Longest-prefix match · Trie vs sorted list · Allow/deny · Rule overlap · match(ip) API",
        "Deterministic LPM; deny/allow with explicit default; thread-safe rule updates if required",
    ),
    section_1(
        goal="Design an **IPv4 CIDR firewall** supporting allow/deny rules, **longest-prefix match (LPM)**, and `match(ip)` returning decision.",
        what_is="""| Scope | Single matcher library | Stateful firewall appliance |
| Rules | CIDR blocks + action | Application-layer rules |
| Match | LPM on IPv4 | IPv6 Phase 2 |
| Databricks lens | Network policy / IP allowlists | Full SDN controller |""",
        fr_rows=[
            ("IP format?", "IPv4 dotted quad or uint32", "Normalize to 32-bit"),
            ("Rule format?", "CIDR + ALLOW/DENY", "Parse '10.0.0.0/8'"),
            ("Overlap?", "More specific prefix wins (LPM)", "Same prefix last-wins or error"),
            ("Default?", "Implicit DENY or ALLOW", "State explicitly"),
            ("Structure?", "Binary trie OR sorted prefix list", "O(32) trie vs O(n) scan"),
            ("Updates?", "addRule/remove at startup MVP", "Dynamic updates thread-safe"),
            ("match API?", "match(String ip) -> Action", "O(1) or O(32)"),
            ("Invalid CIDR?", "Reject at add", "Validate prefix length 0-32"),
            ("Host route?", "/32 single host", "Supported"),
            ("0.0.0.0/0?", "Default catch-all", "Lowest priority unless only rule"),
            ("Batch match?", "Optional", "Phase 2"),
            ("Metrics?", "match count by rule id", "Optional"),
        ],
        mvp=[
            "Parse IPv4 and CIDR to (network uint32, prefixLen).",
            "Store rules in binary trie keyed by bit path OR sorted list by prefix desc.",
            "match(ip): LPM walk; return action of longest matching rule.",
            "Default action when no match (DENY typical).",
            "Overlapping rules: longer prefix wins; tie same len → last inserted wins.",
            "addRule validates CIDR.",
        ],
        scope="IPv4 CIDR matcher: longest-prefix match, allow/deny actions, trie or sorted-list implementation, match(ip) API, overlap via LPM.",
        invariant="""match(ip) returns action of the rule with maximum prefix length among all matching rules.
If multiple rules same prefix length match, last inserted rule wins (documented tie-break).
If no rule matches, return configured default action.""",
    ),
    section_2(
        api="""enum Action { ALLOW, DENY }

class CidrFirewall:
  CidrFirewall(Action defaultAction)
  void addRule(String cidr, Action action) throws InvalidCidr
  void removeRule(String cidr)              // optional MVP
  Action match(String ip) throws InvalidIp
  Action matchUint32(int ipBE)

class Rule:
  int network       // upper bits aligned
  int prefixLen
  Action action
  long ruleId""",
        guarantees=[
            ("LPM correctness", "Most specific matching rule wins"),
            ("Deterministic tie-break", "Same prefix: last add wins"),
            ("Default action", "When no match"),
            ("Invalid input rejected", "At add or match parse"),
            ("Thread safety (optional)", "Read-mostly trie snapshot or RW lock"),
        ],
        errors="""InvalidCidr — malformed cidr or prefix > 32
InvalidIp — malformed ip
RuleNotFound — remove missing rule""",
    ),
    section_3(
        classes=[
            ("CidrFirewall", "Public API"),
            ("CidrParser", "Parse ip and cidr strings"),
            ("TrieNode", "children[0], children[1], action?, prefixLen?"),
            ("BinaryTrie", "Insert and LPM lookup"),
            ("SortedRuleList", "Alt: sort by prefixLen desc scan"),
            ("RuleStore", "Metadata + tie-break order"),
        ],
        diagram="""addRule → parse → Trie.insert(network, len, action)
match(ip) → Trie.lpm(ip) → Action or default

Trie node at depth d: if d==prefixLen store action; continue bit walk""",
    ),
    section_4("""### 4.1 CIDR normalization

```text
network = ip & mask(prefixLen)
mask(p): top p bits 1, rest 0
```

### 4.2 Trie LPM

```text
insert(network, len, action):
  walk bit by bit from MSB for len bits
  mark node at depth len with action (and prefixLen)

lpm(ip):
  best = null
  walk 32 bits; at each node if node.action set and node.prefixLen >= best.prefixLen:
    best = node
  return best?.action ?? default
```

### 4.3 Sorted list alternative

```text
rules sorted by prefixLen descending
for r in rules:
  if ip in r.cidr: return r.action
return default
```

| Structure | match time | add time | Space |
|-----------|------------|----------|-------|
| Trie | O(32) | O(32) | O rules × 32 |
| Sorted list | O(n) | O(n log n) | O(n) |

Choose trie for many rules; list OK for small n in interview."""),
    section_5(
        "| Trie | immutable snapshot OR RWLock on update |\n| match | lock-free read snapshot |",
        ["LPM returns longest prefix match.", "Default only if no node matched.", "Network stored normalized.", "Invalid rules never inserted.", "match doesn't modify state."],
        "update lock → build new trie → atomic swap pointer (readers lock-free)",
    ),
    section_6([
        ("insert trie", """node = root
for bit in 0..prefixLen-1:
  b = (network >> (31-bit)) & 1
  node = node.child[b] or create
  network <<= 1 conceptually
node.action = action
node.prefixLen = prefixLen"""),
        ("lpm", """node = root; best = null
for bit in 0..31:
  if node.action != null and node.prefixLen >= best?.prefixLen:
    best = node
  if node.child[bit(ip,bit)] == null: break
  node = child
return best?.action ?? defaultAction"""),
        ("parse cidr", """parts = split('/')
ip = parseIpv4(parts[0])
len = int(parts[1])
network = ip & mask(len)
return (network, len)"""),
        ("overlap example", """10.0.0.0/8 DENY
10.0.1.0/24 ALLOW
match 10.0.1.5 → ALLOW (longer prefix)"""),
    ]),
    section_7([
        ("Overlapping same length", "Last-wins tie-break", "Document"),
        ("Invalid ip string", "InvalidIp at match", "No partial match"),
        ("Concurrent add/match", "Snapshot swap", "Readers see old or new"),
        ("Memory blow-up sparse trie", "Compress paths Phase 2", "Patricia trie"),
        ("Endianness bug", "Normalize uint32 BE", "Test known ips"),
    ]),
    section_8(
        ["/32 host match", "0.0.0.0/0 default", "LPM specificity", "non-matching ip → default", "invalid cidr rejected", "10/8 vs 10.0.0.0/8 equivalent normalize"],
        ["concurrent match during add with snapshot", "many threads match read-only"],
        None,
    ),
    section_9("Patricia trie compression; IPv6 128-bit; rule indexing by priority ID; hardware TCAM analogy at scale."),
    section_10(
        ["LPM via trie or sorted rules", "Allow/deny per rule", "Default when no match", "Overlap = longer prefix wins"],
        [("Trie MVP", "Patricia / IPv6"), ("Static rules", "Hot reload snapshot")],
        ["Wrong bitmask", "First match not longest", "Forgot default deny"],
    ),
    section_11(
        ["Trie vs sorted list tradeoff?", "How test LPM?", "Deny list vs allow list default?", "CIDR aggregation?", "Rule conflict detection?"],
        [("First rule wins", "Longest prefix"), ("Skip validation", "Reject bad CIDR at add")],
    ),
    section_12(common_appendices("cidr-firewall-matcher")),
]))
