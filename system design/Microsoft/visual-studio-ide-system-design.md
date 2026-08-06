# System Design: Visual Studio–like IDE

> **Focus areas:** Editor buffer · LSP language services · Project/solution model · Extensions · Debugger · Build · Cloud/remote agents · Copilot inline · Sync settings · Performance  
> **Style:** Desktop + service HLD with progressive scale (10× → 100× → 1,000× users/extensions/repos)  
> **Quality bar:** Split UI thread vs language servers vs cloud; latency budgets for typing; deal-breakers for editor jank  
> **Interview theme:** Microsoft — **Visual Studio–class IDE** (HLD). Companion LLD for editor class model: [`ide-editor-class-model-lld-system-design.md`](./ide-editor-class-model-lld-system-design.md)

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

Goal: design a **Visual Studio–like integrated development environment**—multi-file editor, project/solution system, language intelligence, build/debug, extensions, optional remote/dev-box workflows, and Copilot-assisted coding—optimized for **typing latency** and large codebases, with Microsoft ecosystem hooks (Entra accounts, Azure, Copilot).

### 1.0 HLD vs LLD (say this early)

| Track | This doc | Sibling LLD |
|-------|----------|-------------|
| Focus | Processes, services, IPC, scale, cloud | Classes: Buffer, Cursor, Selection, Command, Undo |
| Deliverable | Architecture + trade-offs | Object model + patterns (Command, Observer) |
| When interviewer wants code | Point to sibling; sketch interfaces | Full LLD session |

**Scope statement:** HLD for VS-like IDE product architecture; editor buffer class design lives in the LLD sibling.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Platforms? | Windows first; Mac secondary; web/remote optional | Shell abstraction |
| F2 | Editor? | Multi-caret, folding, diff, large files | Piece table / rope; virtualization |
| F3 | Languages? | C#, C++, Python, JS/TS, more via LSP | Language server host |
| F4 | Projects? | Solutions, projects, references, multi-repo | Workspace model |
| F5 | Build? | MSBuild / cmake / generic tasks | Task runners |
| F6 | Debug? | Breakpoints, step, watch, multi-process | Debug adapter protocol |
| F7 | Git? | Built-in source control UX | SCM provider API |
| F8 | Extensions? | Marketplace; sandboxed | Extension host |
| F9 | Copilot? | Inline completions + chat | Local context + regional AI (see Copilot doc) |
| F10 | Settings sync? | Roam settings across machines | Cloud settings w/ Entra |
| F11 | Remote? | Open folder on SSH / Dev Box / Codespaces-like | Remote agent |
| F12 | Collaboration? | Optional Live Share–like | CRDT/session service Phase 2 |

**MVP functional scope:**

1. Open folder/solution; file tree; multi-tab editor.  
2. Typing with syntax highlight; LSP diagnostics/completion.  
3. Build + problem list; simple run.  
4. Debug with breakpoints (DAP).  
5. Git status/diff/commit basic.  
6. Extension host (trusted + restricted modes).  
7. Copilot inline completions stub (context pack + regional API).  
8. Settings + keymap; optional Entra settings sync.  
9. Remote agent open-SSH Phase 1.5.  
10. Performance: 60 FPS typing on large files with virtualization.

**Out of MVP:** full Live Share product, perfect C++ IntelliSense parity deep dive, entire Marketplace trust & billing, profiler suite completeness.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Keystroke → paint | p99 < 16ms local path (no await network on UI thread) |
| N2 | Completion popup | p50 < 100ms; p99 < 300ms local LSP |
| N3 | Copilot suggest | TTFT < 500ms typical; never block typing |
| N4 | Startup to usable editor | < 3–5s warm for medium solution |
| N5 | Large file | 100 MB+ open with virtualization; no full materialize |
| N6 | Extension isolation | Crash extension ≠ crash UI |
| N7 | Security | Workspace trust; secret scanning hooks; Entra auth for cloud |
| N8 | Offline | Core edit/build local works offline |
| N9 | Reliability | Crash recovery of unsaved buffers |
| N10 | Accessibility | Screen reader + keyboard first-class |

### 1.3 Cases

**Happy**

1. Open solution → restore editors → type → completions → F5 debug.  
2. Install extension → activate on language → adds commands.  
3. Copilot ghost text → Tab accept → telemetry (privacy-respecting).  
4. Remote SSH folder → local UI, remote FS/LSP.  
5. Settings sync via Entra account.

**Edges**

| Case | Behavior |
|------|----------|
| 2 GB log file opened | Virtualize; disable expensive features |
| LSP crash loop | Restart with backoff; show banner |
| Extension infinite CPU | Extension host throttle/kill |
| Untrusted workspace | Restricted mode; no auto tasks/extensions |
| Copilot region outage | Degrade silently to local IntelliSense |
| Network FS latency | Aggressive local cache; debounce |
| Multi-root workspace | Per-folder trust + LSP |
| Undo across Copilot accept | Single undo unit |
| Debuggee exits | DAP session terminate cleanly |
| UI thread blocked by sync I/O | Detect; treat as P0 bug |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU developers | 5M | 50M | — | mega-install base |
| Concurrent Copilot req/s (global) | 20K | 200K | 2M | see Copilot doc |
| Extensions in marketplace | 10K | 100K | — | trust & scanning scale |
| Files in monorepo | 100K | 1M | 10M | indexing architecture |
| Open editors typical | 10 | 10–50 | — | memory management |
| Language servers / session | 2–5 | 10+ | — | host pooling |
| Remote agents | 0–1 | many Dev Boxes | fleet | see cloud-devbox themes |
| Crash reports / day | 100K | 1M | 10M | telemetry pipeline |

**Jumps:** 10× users → cloud services (sync, marketplace, Copilot); 100× repo size → scalable indexing; 1,000× → distributed language intelligence + remote-first.

### 1.5 Scope repeat-back

> Design a VS-like IDE HLD: responsive editor shell, project model, LSP/DAP, build tasks, extension host, Copilot integration via regional AI, optional remote agent, Entra settings sync—keeping UI thread sacred. Editor class LLD is a sibling document.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes (split!)

| Class | Where | Budget |
|-------|-------|--------|
| Keystrokes | Local UI | microseconds–ms |
| Document mutate | Local buffer | ms |
| LSP messages | IPC local | 10–100ms |
| Copilot HTTP | Network regional | 100–800ms async |
| Indexing | Background | minutes for huge repos |
| Telemetry | Async batch | best effort |
| Settings sync | Occasional | seconds |

**Anti-pattern:** designing the IDE as if every keystroke is a distributed transaction.

### 2.2 Typing math

```text
Fast typist ≈ 10 keys/s; bursts higher
Each key: mutate buffer + invalidate + re-render visible lines + schedule lex/LSP
UI budget 16ms/frame ⇒ must not call network synchronously
```

### 2.3 Memory

```text
Piece table / rope for 100 MB file ≪ 100 MB RAM if not fully tokenized
Tokenization: visible window + lookahead
1000 files open eagerly = death; open on demand + LRU
```

### 2.4 LSP traffic

```text
didChange per keystroke debounced 50–150ms OR incremental
Completion: on trigger chars / explicit
Diagnostics: push from server
Monorepo: prefer project subset + file watchers
```

### 2.5 Copilot context pack

```text
Prefix/suffix ≈ 2–8K tokens + open-tab snippets + sibling outlines
Client retrieves; server must honor residency (Entra tenant / geo)
Never block Enter key on Copilot
```

### 2.6 Startup

```text
Cold: shell + extensions activation events (lazy) + solution load async
Aim: editor chrome visible fast; solution hierarchy progressive
```

---

## 3. High-Level Design

### 3.1 Process architecture (critical)

| Process | Responsibility | Crash impact |
|---------|----------------|--------------|
| Main / UI | Windows, editor views, commands | User-visible |
| Extension Host | 3rd party extensions | Isolated restart |
| Language Server(s) | Per-language intelligence | Feature loss |
| Debug Adapter | Talk to debuggee | Debug session |
| Remote Agent | FS, terminals, servers on remote | Remote features |
| Search Indexer | Background index | Search degrade |

**Deal-breaker:** running untrusted extension code on the UI thread in-proc without isolation (modern VS Code–style lessons; classic VS has different history—discuss trade-offs honestly).

### 3.2 HLD options for extension isolation

#### Option A — In-proc plugins (classic)

| Pros | Cons |
|------|------|
| Fast, deep integration | Stability/security risk |

#### Option B — Out-of-proc extension host (chosen for modern design)

| Pros | Cons |
|------|------|
| Crash isolation; permission model | IPC overhead |

#### Option C — Wasm sandbox per extension

| Pros | Cons |
|------|------|
| Strong sandbox | Compatibility / perf engineering |

**Choice:** **B** for MVP design talk; mention C as future hardening.

### 3.3 Editor subsystem (HLD; classes in LLD sibling)

```text
View (virtualized lines)
  → EditorModel / Document
       → Buffer (piece table / rope)  // see LLD
       → EditStack (undo/redo)
       → Decorations / Diagnostics overlay
       → Cursor / Selection state
```

**Protocols of note:** changes as incremental edits; snapshots for LSP versions.

**Pointer:** For `Buffer`, `Command`, `Selection`, composite documents—use [`ide-editor-class-model-lld-system-design.md`](./ide-editor-class-model-lld-system-design.md).

### 3.4 Workspace / solution model

```text
Workspace
  ├── Folder[] / Project[]
  ├── Solution (VS-style) optional graph
  ├── Tasks / Launch configs
  ├── Trust state
  └── Extension enablement per workspace
```

MSBuild project system can be a specialized provider; folder mode is generic.

### 3.5 Language intelligence

Prefer **LSP** for polyglot:

```text
Editor --IPC--> Language Client --stdio/socket--> Language Server
Messages: initialize, textDocument/didOpen/didChange,
  completion, hover, definition, references, publishDiagnostics
```

| Approach | Pros | Cons |
|----------|------|------|
| Built-in only | Perf | Not extensible |
| LSP (chosen) | Ecosystem | Process mgmt |
| Roslyn in-proc for C# | Deep .NET | Special case OK |

**Hybrid:** Roslyn-class deep integration for C#; LSP for others.

### 3.6 Debug

Use **DAP** (Debug Adapter Protocol):

```text
UI ↔ Debug Session ↔ Debug Adapter ↔ Debuggee / runtime
Breakpoints, stackTraces, variables, evaluate, continue/step
```

### 3.7 Build / tasks

```text
TaskProvider (MSBuild, npm, cmake)
  → Terminal execution
  → ProblemMatchers → Problems panel
  → Codelens / error squiggles
```

### 3.8 Copilot integration

```text
InlineCompletionProvider (async)
  → Context builder (prefix, suffix, open files, repo snapshot hashes)
  → Auth (Entra / GitHub)
  → Regional Copilot API (residency-aware)
  → Ghost text render
  → Accept → single undo atom
```

**Never** on UI critical path. Cancel in-flight on further typing (speculative).

Chat/agent mode: separate panel; tool calls to read files with workspace trust checks.

### 3.9 Remote development

```text
Local UI  <==secure channel==>  Remote Agent
                FS, terminals, LSP, debug
```

Local thin client; CPU-heavy language servers remote near code. UX: latency compensation, offline disconnect banners.

### 3.10 Settings sync & identity

- Entra / Microsoft account / GitHub login  
- Sync: keybindings, settings.json, extensions list (not secrets)  
- Conflict: LWW with timestamps + user resolve  
- Enterprise: policy ADMX / Intune-like controls disabling sync or Copilot  

### 3.11 Marketplace

```text
Publish → malware scan → signature → CDN
Client: install → verify signature → extension host load
Enterprise private gallery optional
```

### 3.12 Component list

1. Shell / Workbench  
2. Editor core  
3. Workspace / Project system  
4. Language client hub  
5. Extension host  
6. Task / Build service  
7. Debug service  
8. SCM provider  
9. Search / Indexer  
10. Copilot client  
11. Remote agent protocol  
12. Settings sync service  
13. Telemetry / crashpad  
14. Update channel service  

### 3.13 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Editor buffer | Piece table | Efficient inserts; see LLD |
| UI framework | Platform native + web embeds | VS reality mix; design for abstraction |
| Indexing | Incremental + watchers | Monorepos |
| Copilot | Async speculative | UX |
| Extensions | Out-of-proc | Reliability |
| Remote | Agent protocol | Large cloud repos |

---

## 4. Architecture Diagram

### 4.1 Local process map

```text
+------------------------------------------------------+
| UI / Main Process                                    |
|  Workbench | Editor Views | Command Service          |
+-----+----------------+----------------+--------------+
      |                |                |
      | IPC            | IPC            | IPC
      v                v                v
+-----+------+  +------+-----+  +------+------+
| Extension  |  | Language   |  | Debug      |
| Host       |  | Client Hub |  | Service     |
+-----+------+  +------+-----+  +------+------+
      |                |                |
      |                v                v
      |         +------+-----+   +------+------+
      |         | LSP Server |   | DAP Adapter |
      |         | (C#/TS/..) |   +------+------+
      |         +------------+          |
      v                                 v
+-----+------+                    +-----+------+
| Ext APIs   |                    | Debuggee   |
+------------+                    +------------+

Background: Indexer | Search | Git | Crash reporter
```

### 4.2 Copilot path

```text
Editor keystroke
  -> local IntelliSense (LSP)   [fast path]
  -> debounce Copilot request   [slow path]
       -> ContextBuilder
       -> Regional Copilot API (Entra auth)
       -> ghost text / list
Cancel if document version advanced
```

### 4.3 Remote

```text
+-------------+         +------------------+
| Local UI    |<--mux-->| Remote Agent     |
| editors     |  SSH/   | FileService      |
| thin FS UX  |  relay  | Terminals        |
+-------------+         | LSP/DAP hosts    |
                        | Build tools      |
                        +------------------+
```

### 4.4 Settings sync

```text
IDE -> Sync Client -> Cloud Settings Svc (Entra)
                      | encrypted blob per user
                      | policies from tenant admin
```

### 4.5 Command / keybinding pipeline

```text
Key chord -> KeybindingService -> CommandService
  -> when-clause context (editorFocus, langId, ...)
  -> handler (editor | workbench | extension)
  -> Edit transaction if buffer mutation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **UI thread never awaits network** for core typing.  
2. Document versions monotonic; LSP edits apply only if version matches.  
3. Extension host crash restarts; dirty buffers preserved in main.  
4. Crash recovery files for unsaved docs.  
5. Workspace trust gates tasks/extensions/Copilot tools.  
6. Secrets not written to shared logs; secret scan on commit hooks optional.  
7. Copilot cancel on stale versions; no double-apply.  
8. Debug adapters sandboxed from arbitrary extension influence where possible.  
9. Updates signed; extensions signed/verified.  
10. Remote disconnect doesn’t corrupt local unsaved state.

### 5.2 Scalability (product & codebase)

| Scale | Moves |
|-------|-------|
| 1× | Single folder; 1–2 LSPs; local Git |
| 10× | Solution project system; extension marketplace; Copilot |
| 100× | Monorepo index sharding; remote agents; enterprise policy |
| 1,000× | Cloud language services; multi-agent Dev Boxes; global Copilot capacity |

### 5.3 Maintainability

- Protocol-first (LSP/DAP/remote) reduces bespoke per-language UI.  
- Extension API semantic versioning.  
- Feature flags for editor experiments.  
- Performance goldens: typing latency CI tests.  
- Clear ownership: Editor vs Project vs Debugger vs Copilot.

### 5.4 Progressive narrative

**1×:** Notepad++-plus with LSP.  
**10×:** VS-class solution + debug + extensions.  
**100×:** Enterprise monorepo + remote + policy.  
**1,000×:** AI-native IDE with agents, still 16ms typing.

### 5.5 Buffer & rendering deep dive (HLD)

- **Piece table / rope** for edits (details in LLD).  
- View only materializes viewport lines + cache.  
- Tokenization incremental (Tree-sitter or classifier).  
- Decorations as separate layer (diagnostics, breakpoints, Copilot).  
- IME / accessibility composition events handled carefully.

### 5.6 Latency budgets

```text
Keydown
  0.5ms  map keybinding
  1ms    buffer mutate + undo push
  2ms    schedule re-tokenize visible
  2ms    layout / paint glyphs
  rest   headroom
LSP didChange: async after debounce
Copilot: async; show when ready if still current
```

### 5.7 Indexing & search

```text
Watcher -> incremental parse/index -> inverted index on disk
Query: filename, symbol (from LSP workspaceSymbol), text grep
Huge repos: respect .ignore; remote index side-car
```

### 5.8 Extension API surface

| API | Risk |
|-----|------|
| Commands / views | Low |
| FS read workspace | Medium |
| FS write / exec tasks | High — trust |
| Network | Medium — consent |
| Debug | High |

Restricted mode allowlists.

### 5.9 Copilot context & privacy

- User/tenant policy may disable  
- Content exclusion (`.copilotignore`, secret paths)  
- Enterprise data residency via regional endpoints  
- Telemetry opt levels  
- Snippet retention policies documented  

Cross-link: [`regional-ai-copilot-prompts-system-design.md`](./regional-ai-copilot-prompts-system-design.md)

### 5.10 Multi-root & monorepo

- Per-folder language servers or multi-root aware servers  
- Memory caps; recycle LRU servers  
- Build only affected projects  

### 5.11 Crash & update

- Collect stacks with privacy scrubbing  
- Collect leftover recovery files  
- Background updater; restart-to-update  
- Extension bisect UX for regressions  

### 5.12 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Sync LSP on UI thread | Jank / “IDE frozen” |
| Load whole 1GB file into string | OOM |
| Trust all workspace tasks | Supply chain RCE |
| Copilot blocks Enter | UX disaster |
| Extensions in-UI-proc only | One bad ext kills IDE |
| No document versioning | Corrupt LSP apply |
| Settings sync of tokens | Credential leak |
| Remote without reconnect state | Lost work |

### 5.13 Observability

- Typing latency histograms (local)  
- LSP request durations  
- Extension host CPU  
- Copilot accept rate / cancel rate  
- Crash-free sessions  
- Cold start time  

### 5.14 Security threat model

| Threat | Mitigation |
|--------|------------|
| Malicious extension | Permissions, review, signature, sandbox |
| Malicious repo (`.vscode` tasks) | Workspace trust |
| Man-in-middle updates | Code signing |
| Copilot exfil via prompts | DLP / exclusion / enterprise controls |
| Remote agent takeover | Auth, key mgmt, idle timeout |

### 5.15 Accessibility & intl

- Full keyboard navigation  
- Screen reader announcements for diagnostics  
- RTL / complex script editing collaboration with buffer model  
- High contrast themes  

### 5.16 Collaboration (Phase 2 sketch)

Live Share–like: session relay; share LSP results carefully; privacy for unsynced files; CRDT or OT for concurrent edits—don’t deep-dive unless asked.

### 5.17 Classic VS vs VS Code architecture talk track

Interviewers may compare:

- **Visual Studio**: deep project systems, debugger, designers; historically heavier in-proc extensibility (VSSDK).  
- **VS Code**: web-tech workbench, extension host isolation, LSP-native.  

A strong answer designs **isolation + protocols** while acknowledging VS’s deeper .NET project/debugger integration as specialized services—not pure LSP-only dogma.

---

## 6. Wrap-Up

### 6.1 Designed

A Visual Studio–like IDE HLD: multi-process workbench, virtualized editor, workspace/solution model, LSP/DAP, tasks, isolated extensions, Copilot async client, remote agent, Entra settings sync—UI latency sacred. Editor OO model deferred to LLD sibling.

### 6.2 Decisions to defend

1. UI thread purity  
2. Piece table + view virtualization  
3. LSP/DAP protocols  
4. Out-of-proc extension host  
5. Workspace trust  
6. Async Copilot with version cancel  
7. Hybrid Roslyn + LSP  
8. Remote agent split  
9. Signed updates/extensions  
10. Explicit HLD/LLD split for interviews  

### 6.3 Risks

- Monorepo scale  
- Extension ecosystem abuse  
- Copilot quality vs privacy  
- Remote latency  
- Project system complexity (MSBuild)  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | HLD vs LLD sibling; typing SLO |
| 5–15 | Process architecture + editor HLD |
| 15–25 | LSP/DAP/build |
| 25–35 | Extensions trust + Copilot |
| 35–45 | Remote, scale, deal-breakers |

### 6.5 Closer

> **VS-like IDE**: keep typing local and fast, push intelligence to LSP/DAP/Copilot asynchronously, isolate extensions, trust workspaces, sync settings with Entra—and park buffer class details in the LLD sibling when the interviewer wants code.

---

## 7. Deeper / Related Interview Questions

### 7.1 Editor

**Q: Array of lines vs piece table vs rope?**  
A: Arrays painful for mid-file inserts; piece table classic for editors; ropes also valid—defend mutability + undo. Details in LLD.

**Q: How do you handle multi-cursor edits?**  
A: Transaction applies ordered non-overlapping ranges; single undo unit.

### 7.2 LSP

**Q: Full document sync vs incremental?**  
A: Incremental for large files; watch server capabilities.

**Q: Stale completion apply?**  
A: Bind to document version; discard if mismatch.

### 7.3 Performance

**Q: IDE freezes on paste of huge text.**  
A: Chunk apply; defer tokenization; virtualize; maybe warn.

### 7.4 Extensions

**Q: How do you stop `while(true)` in an extension?**  
A: Separate process; CPU watchdog; kill + disable.

### 7.5 Copilot

**Q: What context is sent?**  
A: Configurable; exclusions; enterprise residency; show UI affordances.

**Q: Ghost text vs list UX under latency?**  
A: Speculative; cancel; don’t steal cursor.

### 7.6 Remote

**Q: Where should LSP run?**  
A: Near files (remote) to reduce chattiness; UI local.

### 7.7 Comparison traps

**Q: Is this just VS Code?**  
A: Architecture rhymes; VS differentiates project/debugger depth + Microsoft ecosystem integration.

**Q: Why not browser-only IDE?**  
A: Valid remote-first variant; still need agent + latency story; native debugger integrations harder.

### 7.8 Failure injection

1. LSP killed every 5s.  
2. Extension host OOM.  
3. Disk full during recovery write.  
4. Copilot 5s latency.  
5. Untrusted repo with preLaunchTask format C:.  
6. Network FS 500ms RTT.  
7. Invalid UTF-8 / binary file.  
8. Debugger attach race.  
9. Settings sync conflict.  
10. Clock skew on document timestamps.

### 7.9 Extra traps

- What runs on the UI thread?  
- How is undo stored across Copilot + user edits?  
- How do you sandbox terminal commands from extensions?  
- What’s the update trust chain?  
- How do you measure typing latency in production?  
- When do you shed language services under memory pressure?  
- How does accessibility announce completion UI?  
- How do solution load failures partial-render?  
- What’s in a crash dump from a customer enterprise machine?  
- How do you migrate settings across major versions?

### 7.10 LLD transition cues

If interviewer says “code the editor,” switch to sibling:

- Classes: `Document`, `PieceTable`, `Range`, `Selection`, `EditCommand`, `UndoStack`, `EditorView`  
- Patterns: Command, Observer/events, Iterator for lines  
- Tests: insert/delete/undo; multi-cursor; snapshot versions  

### 7.11 Related Microsoft prompts

- Regional Copilot prompts  
- Cloud Dev Box (OpenAI sibling themes / Microsoft Dev Box)  
- File system classes LLD  
- Chat/messaging (Live Share relay analogies)  
- OTA/update orchestration (IDE updater)  

---

## 8. Appendices

### Appendix A — Document version protocol sketch

```text
Document {
  uri, languageId,
  version: int,          // increments each edit
  buffer,
  lspSyncedVersion
}

applyEdit(edit):
  version++
  buffer.apply(edit)
  undoStack.push(...)
  scheduleViewUpdate()
  scheduleLspDidChange(version)
```

### Appendix B — IPC message examples

```json
{ "type": "editor/didChange", "uri": "file:///...", "version": 42,
  "changes": [{"start": 10, "end": 10, "text": "x"}] }

{ "type": "ext/command", "id": "eslint.fix", "args": [] }
```

### Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Editor + LSP + tasks + debug basic |
| 10× | Extension host, marketplace client, Copilot client, SCM |
| 100× | Monorepo index, remote agent, enterprise policy, trust |
| 1,000× | Cloud assist services, agentic workflows, global Copilot ops |

### Appendix D — Glossary

| Term | Meaning |
|------|---------|
| LSP | Language Server Protocol |
| DAP | Debug Adapter Protocol |
| Piece table | Buffer data structure (see LLD) |
| Extension host | Isolated process for extensions |
| Workspace trust | Safety gate for repos |
| Ghost text | Inline Copilot suggestion |
| Project system | MSBuild/solution graph integration |
| Remote agent | Server-side IDE services near code |
| Workbench | Overall IDE chrome |
| Problem matcher | Parse build output to diagnostics |

### Appendix E — Estimation cheat-sheet

```text
Typing ≠ Copilot QPS ≠ Marketplace downloads

UI budget ≈ 16ms/frame
LSP debounce 50–150ms
Copilot always async + cancellable
Large file: virtualize view + incremental tokenize
```

### Appendix F — Command when-clause examples

```text
editorTextFocus && !editorReadonly && editorLangId == 'csharp'
debuggersAvailable && inDebugMode
workspaceTrustState == 'trusted'
```

### Appendix G — Copilot request (client sketch)

```http
POST /v1/copilot/completions
Authorization: Bearer ...
{
  "document": {"uri":"...", "version":42, "language":"csharp"},
  "position": {"line":10,"character":15},
  "prefix": "...",
  "suffix": "...",
  "extras": {"open_tabs":[...], "exclusions_honored":true}
}
```

### Appendix H — Interview whiteboard order

1. Process map (UI / ext / LSP / DAP)  
2. Typing latency path  
3. Buffer + view virtualization (HLD)  
4. Workspace trust  
5. Copilot async  
6. Remote optional  
7. Point to LLD for classes  

### Appendix I — MVP feature cut list

**In:** edit, LSP, build, debug, git basic, extensions, Copilot stub, settings  
**Out:** Live Share, full profiling, designers, mobile IDE  

### Appendix J — Mapping to Microsoft ecosystem

| Concern | Microsoft hook |
|---------|----------------|
| Identity | Entra / MSA / GitHub |
| AI | GitHub Copilot / Copilot Chat regional APIs |
| Cloud dev | Microsoft Dev Box / Azure VMs |
| Policy | Intune / enterprise admin |
| Telemetry | Privacy-preserving Crashes/CEIP toggles |
| .NET depth | Roslyn, MSBuild, VS debugger engines |

### Appendix K — LLD sibling bridge

When switching sessions:

1. Freeze HLD process map.  
2. Open LLD: implement `PieceTable` + `UndoStack` + `Editor` commands.  
3. Show how `version` increments plug into LSP.  
4. Do **not** re-litigate cloud Copilot in LLD time unless asked.

---

*End of design doc. Open with HLD/LLD split + typing SLO; whiteboard §4; close with deal-breakers §5.12; hand off to LLD sibling for class model.*
