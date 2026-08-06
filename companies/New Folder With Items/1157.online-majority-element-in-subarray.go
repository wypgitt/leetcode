package leetcode

import "sort"

//
// LeetCode 1157 — Online Majority Element In Subarray
//
// --- Interview notes (majority + segment tree merge, verification, complexity, constraints, alternatives) ---
//
// Problem
// Preprocess array `arr`. Each query(left, right, threshold) asks: is there a value that appears **at least**
// `threshold` times in arr[left..right] inclusive? Return such a value, or -1. Up to 1e4 queries on |arr| <= 2e4.
//
// Constraint (critical)
// `2 * threshold > (right - left + 1)` i.e. threshold > half the subarray length. So any valid answer would have to be a
// **strict majority** in the usual sense (more than half). At most one distinct value can satisfy the frequency check.
//
// Why not scan each query in O(range length)?
// Worst-case O(queries * n) is too slow for n, queries ~ 1e4–2e4.
//
// Plan — two phases
// (1) **Candidate** x that *could* be the majority on [L, R], in O(log n) time.
// (2) **Verify** frequency of x on [L, R], in O(log n) time. If count >= threshold return x else -1.
//
// Phase 1 — Boyer–Moore majority merge on a segment tree
// Boyer–Moore voting finds a majority element in one pass if one exists (> n/2 copies). For subarrays we cannot afford a
// linear scan per query. Observation: the same “candidate + relative count” pairing can be **merged** like associative
// folds over contiguous blocks (same idea as parallel BM).
//
// Merge two adjacent intervals with summaries (v1, c1) and (v2, c2):
//   • If v1 == v2 → (v1, c1 + c2)
//   • Else if c1 > c2 → (v1, c1 - c2)   # cancel opposing votes
//   • Else → (v2, c2 - c1)
// Leaves store (arr[i], 1). Internal nodes merge children. Range query merges O(log n) canonical segments → O(log n).
//
// If a strict majority exists on [L,R], its value is **always** the candidate produced by this merge (standard fact).
// If no majority exists, the candidate is arbitrary garbage for our purpose — verification fails.
//
// Phase 2 — Frequency via sorted positions per value
// Build `pos[value] = sorted list of indices where arr[index] == value`. Count of value x in [L,R] is:
//   bisect_right(pos[x], R) - bisect_left(pos[x], L)   → O(log n) per query.
//
// Why this data structure for verification?
// • Values up to 20000 — coarse bucket map is fine.
// • Sorted indices + bisect beats scanning and pairs naturally with offline preprocessing O(n).
//
// Time complexity
// • Build positions map: O(n). Build segment tree: O(n).
// • Each query: O(log n) segment-tree walk + O(log n) bisects → **O(log n)**.
//
// Space complexity
// • Positions store each index once: O(n). Segment tree ~4n nodes: **O(n)**.
//
// Edge cases
// • threshold equals subarray length → verify candidate count == length.
// • No majority / frequency below threshold → verification returns -1 even if candidate looks plausible after BM merge.
//
// Tests (statement)
// arr = [1,1,2,2,1,1]
// query(0,5,4) → value 1 appears 4 times → 1
// query(0,3,3) → no value ≥ 3 times in [1,1,2,2] → -1
// query(2,3,2) → [2,2] → 2
//
// Alternative approaches (trade-offs)
// • **Random sampling** (problem hints): sample random indices in [L,R]; check arr[k]. Probability ≥ 1/2 each trial if a
//   majority exists; repeat ~40–60 times for negligible failure — expected O(k log n) per query with verification. Randomized,
//   not deterministic.
// • **Wavelet tree / persistent structures**: heavier; overkill for interviews unless already familiar.
// • **Square decomposition**: O(√n) or similar per query.
//
// Improvements
// • Iterative segment tree to avoid recursion overhead (same asymptotics).
// • Single bisect on `pos[candidate]` after query.
//
// --- end notes ---
//

type majorityPair1157 struct {
	val int
	cnt int
}

// MajorityChecker1157 supports online majority queries with verification.
type MajorityChecker1157 struct {
	arr  []int
	n    int
	pos  map[int][]int
	tree []majorityPair1157
}

func NewMajorityChecker1157(arr []int) *MajorityChecker1157 {
	n := len(arr)
	pos := make(map[int][]int, n)
	for i, x := range arr {
		pos[x] = append(pos[x], i)
	}

	m := &MajorityChecker1157{
		arr:  arr,
		n:    n,
		pos:  pos,
		tree: make([]majorityPair1157, 4*maxInt(1, n)),
	}
	if n > 0 {
		m.build(1, 0, n-1)
	}
	return m
}

func (m *MajorityChecker1157) merge(a, b majorityPair1157) majorityPair1157 {
	v1, c1 := a.val, a.cnt
	v2, c2 := b.val, b.cnt
	if v1 == v2 {
		return majorityPair1157{val: v1, cnt: c1 + c2}
	}
	if c1 > c2 {
		return majorityPair1157{val: v1, cnt: c1 - c2}
	}
	return majorityPair1157{val: v2, cnt: c2 - c1}
}

func (m *MajorityChecker1157) build(node, l, r int) {
	if l == r {
		m.tree[node] = majorityPair1157{val: m.arr[l], cnt: 1}
		return
	}
	mid := (l + r) / 2
	m.build(node*2, l, mid)
	m.build(node*2+1, mid+1, r)
	m.tree[node] = m.merge(m.tree[node*2], m.tree[node*2+1])
}

func (m *MajorityChecker1157) queryPair(node, l, r, ql, qr int) majorityPair1157 {
	if ql <= l && r <= qr {
		return m.tree[node]
	}
	if r < ql || l > qr {
		return majorityPair1157{val: 0, cnt: 0}
	}
	mid := (l + r) / 2
	left := m.queryPair(node*2, l, mid, ql, qr)
	right := m.queryPair(node*2+1, mid+1, r, ql, qr)
	return m.merge(left, right)
}

// Query returns the majority element in [left,right] with count >= threshold, else -1.
func (m *MajorityChecker1157) Query(left, right, threshold int) int {
	if m.n == 0 {
		return -1
	}
	cand := m.queryPair(1, 0, m.n-1, left, right).val
	lst := m.pos[cand]
	if len(lst) == 0 {
		return -1
	}
	lo := sort.SearchInts(lst, left)
	hi := sort.Search(len(lst), func(i int) bool { return lst[i] > right })
	if hi-lo >= threshold {
		return cand
	}
	return -1
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

