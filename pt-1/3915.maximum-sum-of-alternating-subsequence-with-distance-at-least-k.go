package leetcode

import "sort"

//
// @lc app=leetcode id=3915 lang=golang
//
// [3915] Maximum Sum of Alternating Subsequence With Distance At Least K
//
// =============================================================================
// OFFICIAL PROBLEM (summary)
// =============================================================================
//
// Pick indices i1 < i2 < … with **i_{t+1} - i_t >= k**. The **values** must form a
// **strictly alternating** sequence in value space:
//   either  nums[i1] < nums[i2] > nums[i3] < …
//   or      nums[i1] > nums[i2] < nums[i3] > …
// Any single element counts as alternating. The **score** is the **sum** of
// chosen values (no +/- parity on signs — “alternating” refers to up/down in
// value, like a zigzag).
//
// =============================================================================
// DP (two states = “last edge direction”)
// =============================================================================
//
// After fixing the last pick at index `j`, only whether **nums[j]** is a **peak**
// or **valley** among the last two selected values matters for what **nums[i]**
// may follow (with `i - j >= k`):
//
// - **high[j]** = best score of a valid subsequence **ending at j** such that
//   if length >= 2, the previous value is **< nums[j]**  (“… < nums[j]” — `j` is
//   a local peak in the value zigzag).
//
// - **low[j]**  = best score ending at `j` with previous **> nums[j]** if length >= 2
//   (“… > nums[j]” — `j` is a local valley).
//
// Length-1 subsequence: both **high[j] = low[j] = nums[j]** (either convention).
//
// Transitions for `i - j >= k` (strict inequalities on values):
// - If **nums[j] < nums[i]** we may extend a **valley** at `j` upward → new peak at `i`:
//     **high[i] = max(high[i], low[j] + nums[i])**
// - If **nums[j] > nums[i]** we may extend a **peak** at `j` downward → new valley at `i`:
//     **low[i] = max(low[i], high[j] + nums[i])**
//
// Base: **high[i] >= nums[i]**, **low[i] >= nums[i]** (take only index `i`).
//
// Answer: **max_i max(high[i], low[i])**.
//
// =============================================================================
// ACCELERATING THE MAX OVER j (segment tree on compressed values)
// =============================================================================
//
// Naive scan over all `j <= i - k` is **O(n^2)**. After processing index `p`,
// index `p` becomes usable as a predecessor when we reach `i = p + k`. Maintain
// two max segment trees over **compressed coordinate of nums[p]**:
//   - tree_low stores at each value coordinate **max low[p]** among inserted `p`;
//   - tree_high stores **max high[p]** among inserted `p`.
//
// At index `i`:
//   1. If **i >= k**, insert index **i - k** into both trees at **nums[i-k]**.
//   2. **high[i] = nums[i]**; **low[i] = nums[i]**.
//   3. **M_lo** = max **low[j]** over inserted `j` with **nums[j] < nums[i]**
//      → prefix max on **tree_low** over value coords **[0, pos(nums[i]) - 1]**.
//      **M_hi** = max **high[j]** over inserted `j` with **nums[j] > nums[i]**
//      → range max on **tree_high** over **[pos(nums[i]) + 1, M-1]**.
//   4. **high[i] = max(high[i], M_lo + nums[i])** if **M_lo** finite;
//      **low[i] = max(low[i], M_hi + nums[i])** if **M_hi** finite.
//
// **Time O(n log n)**, **space O(n)** (trees + compression).
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - **k = 1**: every adjacent index pair allowed (subject to value zigzag).
// - **Large k**: only length-1 subsequences → **max(nums)**.
// - **Equal values**: **nums[j] == nums[i]** forbids extending (strict alternation).
//
// =============================================================================
// COMMON MISTAKE (what went wrong in an earlier draft)
// =============================================================================
//
// Do **not** confuse this with “alternating **sum**” (+a − b + c − … by pick order).
// Here **alternating** means **strict zigzag of values** (< > < > or > < > <); the
// objective is **sum of chosen nums[i]**. Example **nums = [5,4,2], k = 2**:
// pick indices **[0,2]** → values **5 > 2** → score **7**, not **5 − 2**.
//
// =============================================================================
// INTERVIEW TALK TRACK (why this algorithm / data structures)
// =============================================================================
//
// **Why two states (high / low)?**
// After the last picked value `v`, the next admissible value is constrained only
// by whether we must go **up** or **down** from `v`. That is exactly “last step
// was ascending into `v` (peak)” vs “descending into `v` (valley)”.
//
// **Why segment trees (or two Fenwick-style structures), not plain prefix arrays?**
// The predecessor `j` must satisfy **value** inequality (`nums[j] < nums[i]` or
// `>`), not just index order. After restricting to **eligible indices** (inserted
// in order of `i`), we need **max DP over j with nums[j] in a range of values** —
// that is a **2D** constraint (index cutoff via sliding eligibility + value range).
// Coordinate-compress values and use **range max** queries: prefix for `< nums[i]`,
// suffix for `> nums[i]`.
//
// **Why coordinate compression?**
// Values are up to 1e5; segment tree size is **O(#distinct values)** ≤ **n**.
//
// =============================================================================
// COMPLEXITY
// =============================================================================
//
// - **Time:** **O(n log n)** — each index: **O(log n)** updates + queries.
// - **Space:** **O(n)** for DP arrays + **O(m)** for trees (**m** = distinct values).
//
// =============================================================================
// TESTING & VALIDATION
// =============================================================================
//
// For **n ≤ ~15**, brute-force all non-empty index subsets: check gap ≥ **k**,
// verify zigzag on selected values, compare max sum to the algorithm. Randomized
// stress tests catch off-by-one on insertion index **i − k** and strict **<** / **>**.
//
// =============================================================================
// POSSIBLE IMPROVEMENTS / VARIANTS
// =============================================================================
//
// - **Fenwick tree for prefix max** + reversed Fenwick for suffix max (same bounds).
// - If constraints were tiny, **O(n²)** DP is a correct reference implementation.
// - **Merge-sort tree** or **balanced BST** could answer the same queries; segment
//   tree is a standard choice for static compressed coordinates.
//
// =============================================================================

// @lc code=start

type segTreeMax3915 struct {
	n    int
	size int
	neg  int64
	t    []int64
}

func newSegTreeMax3915(n int, neg int64) *segTreeMax3915 {
	size := 1
	for size < n {
		size <<= 1
	}
	t := make([]int64, 2*size)
	for i := range t {
		t[i] = neg
	}
	return &segTreeMax3915{n: n, size: size, neg: neg, t: t}
}

func (st *segTreeMax3915) update(i int, val int64) {
	i += st.size
	if val > st.t[i] {
		st.t[i] = val
	}
	i >>= 1
	for i > 0 {
		a, b := st.t[2*i], st.t[2*i+1]
		if a >= b {
			st.t[i] = a
		} else {
			st.t[i] = b
		}
		i >>= 1
	}
}

func (st *segTreeMax3915) query(l, r int) int64 {
	// Max on inclusive [l, r]; empty range returns neg.
	if l > r {
		return st.neg
	}
	if l < 0 {
		l = 0
	}
	if r >= st.n {
		r = st.n - 1
	}
	if l > r {
		return st.neg
	}
	l += st.size
	r += st.size
	res := st.neg
	for l <= r {
		if (l & 1) == 1 {
			if st.t[l] > res {
				res = st.t[l]
			}
			l++
		}
		if (r & 1) == 0 {
			if st.t[r] > res {
				res = st.t[r]
			}
			r--
		}
		l >>= 1
		r >>= 1
	}
	return res
}

// MaxAlternatingSum3915 returns the maximum sum of a subsequence whose values strictly zigzag
// and consecutive indices differ by at least k.
func MaxAlternatingSum3915(nums []int, k int) int64 {
	n := len(nums)
	vals := make([]int, n)
	copy(vals, nums)
	sort.Ints(vals)
	// unique
	uniq := vals[:0]
	for _, v := range vals {
		if len(uniq) == 0 || uniq[len(uniq)-1] != v {
			uniq = append(uniq, v)
		}
	}
	m := len(uniq)
	coord := make(map[int]int, m)
	for i, v := range uniq {
		coord[v] = i
	}

	const neg int64 = -(1 << 62)
	stLow := newSegTreeMax3915(m, neg)
	stHigh := newSegTreeMax3915(m, neg)

	high := make([]int64, n)
	low := make([]int64, n)
	for i := range high {
		high[i] = neg
		low[i] = neg
	}

	ans := neg
	for i := 0; i < n; i++ {
		if i >= k {
			p := i - k
			posP := coord[nums[p]]
			stLow.update(posP, low[p])
			stHigh.update(posP, high[p])
		}

		pos := coord[nums[i]]
		ml := stLow.query(0, pos-1)
		mh := stHigh.query(pos+1, m-1)

		v := int64(nums[i])
		high[i] = v
		low[i] = v
		if ml != neg && ml+v > high[i] {
			high[i] = ml + v
		}
		if mh != neg && mh+v > low[i] {
			low[i] = mh + v
		}

		if high[i] > ans {
			ans = high[i]
		}
		if low[i] > ans {
			ans = low[i]
		}
	}
	return ans
}

// @lc code=end

