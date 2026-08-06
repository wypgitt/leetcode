package leetcode

import "container/heap"

//
// LeetCode 1172 — Dinner Plate Stacks
//
// --- Interview notes (operations, heaps, lazy deletion, trim, complexity, edges, alternatives) ---
//
// Problem
// Infinitely many stacks in a row, indexed 0, 1, 2, … Each stack holds at most `capacity` plates.
// • push(val) — push onto the **leftmost** stack that still has room (length < capacity). If none exist, open a **new**
//   stack at the **right** end and push there.
// • pop() — pop from the **rightmost** stack that is **non-empty**. Return -1 if everything empty.
// • popAtStack(index) — pop top of stack `index`; return -1 if that stack missing or empty.
//
// Why naive scanning is too slow
// `push` wants min index with space; `pop` wants max index with content. Repeated linear scans over all stacks can be
// O(number of stacks) per call — too slow under ~2·10⁵ operations if stacks grow large.
//
// Data structures
// 1. **`stacks: List[List[int]]`** — dynamic array of stacks (Python list as stack: append / pop from end).
// 2. **`avail` — min-heap** of indices `i` such that we *believe* `len(stacks[i]) < capacity`. Supports “leftmost stack
//    with room”: smallest valid index is heap minimum.
// 3. **`nonempty` — max-heap via negatives** — store `-i` in a min-heap so smallest `-i` corresponds to largest `i`.
//    Gives “rightmost non-empty stack” among recorded candidates.
//
// Lazy deletion (stale heap entries)
// After pops, some heap entries point to stacks that are now full (`avail`) or empty (`nonempty`). Instead of eagerly
// removing them (expensive), **peek/pop from the heap until the top refers to a currently valid index** (still has room /
// still non-empty). Amortized cost stays logarithmic per operation over the sequence.
//
// Trailing empty stacks
// After `pop()` or `popAtStack`, repeatedly drop **only** `stacks[-1]` while it is empty. This keeps the array from growing
// forever with useless trailing shells and keeps “new stack” creation aligned with need. Inner holes (empty stacks before
// the last index) are **kept** — their indices stay valid and remain in `avail` for future `push`.
//
// Algorithm walkthrough
// • **push(val)** — Pop stale tops from `avail`. If empty, append `[]`, push its index onto `avail`. Pop smallest usable
//   index `idx`, append `val`, push `-idx` onto `nonempty`. If stack still has room, push `idx` back onto `avail`.
// • **pop()** — Pop stale tops from `nonempty`. Pop largest valid index `i`, pop plate from `stacks[i]`. If stack now has
//   room, push `i` on `avail`; if still non-empty, push `-i` on `nonempty`. Trim trailing empty stacks.
// • **popAtStack(index)** — Bounds / empty check; pop top; push `index` onto `avail` (slot freed); trim trailing empties.
//
// Time complexity (typical analysis)
// Each operation: O(log K) heap work where K is heap size (bounded by number of operations), plus amortized O(1) trim at
// stack end. Overall **O(log N)** per call with N ~ stack count / operations.
//
// Space complexity
// **O(S)** for stored plates plus **O(H)** for heaps — **O(S + Q)** over Q operations in worst case for heap garbage (still
// acceptable on LC constraints).
//
// Edge cases
// • capacity = 1 — each stack holds one plate; `avail` always tracks singleton holes after pops.
// • pop / popAtStack on empty → -1.
// • Large `index` with sparse stacks — list length check prevents out-of-range.
//
// Tests (statement Example 1)
// capacity 2, sequence push 1..5, popAtStack(0), push 20,21, popAtStack(0), popAtStack(2), then pops → outputs
// 2,20,21,5,4,3,1,-1 as in problem.
//
// Alternatives / improvements
// • **Sorted containers** (TreeSet of indices) — same logarithmic bounds, clearer “valid set” semantics.
// • **Explicit doubly-linked list** of non-empty / non-full stacks — O(1) updates if carefully maintained; more code.
// • **Periodic heap rebuild** if memory of stale entries becomes an issue (rare in contests).
//
// --- end notes ---
//

type intMinHeap1172 []int

func (h intMinHeap1172) Len() int            { return len(h) }
func (h intMinHeap1172) Less(i, j int) bool  { return h[i] < h[j] }
func (h intMinHeap1172) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *intMinHeap1172) Push(x any)         { *h = append(*h, x.(int)) }
func (h *intMinHeap1172) Pop() any           { old := *h; v := old[len(old)-1]; *h = old[:len(old)-1]; return v }
func (h intMinHeap1172) Peek() (int, bool)   { if len(h) == 0 { return 0, false }; return h[0], true }

type intMaxHeap1172 []int // store indices as negative values (like Python)

func (h intMaxHeap1172) Len() int           { return len(h) }
func (h intMaxHeap1172) Less(i, j int) bool { return h[i] < h[j] } // smaller negative => larger index
func (h intMaxHeap1172) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *intMaxHeap1172) Push(x any)        { *h = append(*h, x.(int)) }
func (h *intMaxHeap1172) Pop() any          { old := *h; v := old[len(old)-1]; *h = old[:len(old)-1]; return v }
func (h intMaxHeap1172) Peek() (int, bool)  { if len(h) == 0 { return 0, false }; return h[0], true }

// DinnerPlates1172 implements the DinnerPlates data structure.
type DinnerPlates1172 struct {
	capacity int
	stacks   [][]int
	avail    intMinHeap1172
	nonempty intMaxHeap1172
}

func NewDinnerPlates1172(capacity int) *DinnerPlates1172 {
	d := &DinnerPlates1172{capacity: capacity}
	heap.Init(&d.avail)
	heap.Init(&d.nonempty)
	return d
}

func (d *DinnerPlates1172) Push(val int) {
	for {
		top, ok := d.avail.Peek()
		if !ok {
			break
		}
		if top >= len(d.stacks) || len(d.stacks[top]) >= d.capacity {
			heap.Pop(&d.avail)
			continue
		}
		break
	}
	if d.avail.Len() == 0 {
		d.stacks = append(d.stacks, []int{})
		heap.Push(&d.avail, len(d.stacks)-1)
	}

	idx := heap.Pop(&d.avail).(int)
	d.stacks[idx] = append(d.stacks[idx], val)
	heap.Push(&d.nonempty, -idx)
	if len(d.stacks[idx]) < d.capacity {
		heap.Push(&d.avail, idx)
	}
}

func (d *DinnerPlates1172) Pop() int {
	for {
		top, ok := d.nonempty.Peek()
		if !ok {
			return -1
		}
		i := -top
		if i < len(d.stacks) && len(d.stacks[i]) > 0 {
			break
		}
		heap.Pop(&d.nonempty)
	}

	i := -heap.Pop(&d.nonempty).(int)
	st := d.stacks[i]
	val := st[len(st)-1]
	d.stacks[i] = st[:len(st)-1]

	if len(d.stacks[i]) < d.capacity {
		heap.Push(&d.avail, i)
	}
	if len(d.stacks[i]) > 0 {
		heap.Push(&d.nonempty, -i)
	}
	for len(d.stacks) > 1 && len(d.stacks[len(d.stacks)-1]) == 0 {
		d.stacks = d.stacks[:len(d.stacks)-1]
	}
	return val
}

func (d *DinnerPlates1172) PopAtStack(index int) int {
	if index >= len(d.stacks) || len(d.stacks[index]) == 0 {
		return -1
	}
	st := d.stacks[index]
	val := st[len(st)-1]
	d.stacks[index] = st[:len(st)-1]
	heap.Push(&d.avail, index)
	for len(d.stacks) > 1 && len(d.stacks[len(d.stacks)-1]) == 0 {
		d.stacks = d.stacks[:len(d.stacks)-1]
	}
	return val
}

