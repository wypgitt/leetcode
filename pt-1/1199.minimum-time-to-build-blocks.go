package leetcode

import "container/heap"

//
// LeetCode 1199 — Minimum Time To Build Blocks
//
// --- Interview notes (workers/splits, reverse simulation, min-heap greedy, complexity, examples, pitfalls) ---
//
// Problem (rules)
// • Each block `blocks[i]` takes that many time units for **one** worker to build (blocks run in parallel across workers).
// • Start with **one** worker at time 0.
// • A worker may **split** into two workers: global clock advances by `split` for that split (parallel splits at the same
//   instant still each pay `split` — here only one worker splits at a time in the optimal schedule story).
// • After splitting, you have one extra worker; workers may build blocks or split again until every block is assigned and
//   finished.
// • Goal: **minimum makespan** — time when the **last** block finishes.
//
// Forward scheduling is messy (many split/build interleavings). **Reverse view — merge blocks instead of splitting workers**
// Pair two unfinished “jobs” into one composite job: if forward you had split then eventually built the two subtrees, going
// backward you **merge** two blocks `a` and `b` into a single representative whose completion time is `split +
// max(a,b)` — first pay split to duplicate labor, then the slower block dominates parallel completion (matches Example 2:
// `split + max(block times)` when only two blocks).
//
// Greedy choice (core invariant)
// Among pending jobs, **always merge the two smallest remaining build times first** (always discard the globally cheapest
// block as one side of the merge — implemented by popping the minimum twice but combining only the second with `split`;
// equivalent Huffman-style greedy). Long-running blocks should participate in **fewer** merges so they are not repeatedly
// inflated by `split`; processing cheap blocks early minimizes repeated `split` accumulation on heavy tasks.
//
// Algorithm (min-heap, editorial-equivalent loop)
// Put all `blocks[i]` in a **min-heap**.
// While more than one element remains:
//   1. `heappop` — drop the smallest pending job (pair it implicitly with the next smallest).
//   2. `second = heappop`; `heappush(second + split)` — merged virtual job replaces those two.
// When one number remains, it equals the optimal makespan.
//
// Correctness sketch
// Formal proof matches Huffman-type exchange on merge trees / optimal binary trees with additive edge cost `split`. The
// heap simulation is the linear-time-known greedy for this merge cost structure.
//
// Data structures
// • **Binary min-heap** (`heapq`) — repeated extract-min and insert in **O(log n)** per step, **n−1** merges → **O(n log n)**.
//
// Time complexity **O(n log n)** (heap operations dominate).
//
// Space complexity **O(n)** for the heap (copy `blocks` if mutating inputs is undesirable).
//
// Edge cases
// • **Single block** — loop skipped; answer is `blocks[0]` (only build, no split).
// • **Large `split`** — merges inflate mostly by `split`; greedy still applies.
//
// Tests (statement)
// • `blocks = [1]`, `split = 1` → **1**.
// • `blocks = [1,2]`, `split = 5` → **7** (`split + max(1,2)`).
// • `blocks = [1,2,3]`, `split = 1` → **4** (see statement expansion).
//
// Pitfalls
// • Do **not** use `max(a + split, b)` by popping two mins unless it matches this problem’s merge semantics — the approved
//   pattern is **pop min, pop next, push next + split** (equivalent to the editorial merge rule for this model).
// • Copy the array before `heapify` if callers must keep `blocks` immutable.
//
// Improvements
// • `heapq.merge` not needed — single heap suffices.
// • For integer weights only, radix buckets possible in theory; heap is standard.
//
// --- end notes ---
//

type intMinHeap1199 []int

func (h intMinHeap1199) Len() int            { return len(h) }
func (h intMinHeap1199) Less(i, j int) bool  { return h[i] < h[j] }
func (h intMinHeap1199) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *intMinHeap1199) Push(x any)         { *h = append(*h, x.(int)) }
func (h *intMinHeap1199) Pop() any           { old := *h; v := old[len(old)-1]; *h = old[:len(old)-1]; return v }

// MinBuildTime1199 returns the minimum time to build all blocks.
func MinBuildTime1199(blocks []int, split int) int {
	h := make(intMinHeap1199, len(blocks))
	copy(h, blocks)
	heap.Init(&h)
	for h.Len() > 1 {
		heap.Pop(&h)
		second := heap.Pop(&h).(int)
		heap.Push(&h, second+split)
	}
	return h[0]
}

