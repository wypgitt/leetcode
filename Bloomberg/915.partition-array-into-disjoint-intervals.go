package leetcode

//
// @lc app=leetcode id=915 lang=golang
//
// [915] Partition Array into Disjoint Intervals
//

// =============================================================================
// INTERVIEW: ELEVATOR PITCH (~30 seconds)
// =============================================================================
//
// "Split the array into a non-empty prefix I and suffix J so every value in I is
// ≤ every value in J. Equivalently, max(I) ≤ min(J). The smallest such prefix is
// found by scanning left to right: whenever we see a value **smaller** than the
// maximum we're forced to keep on the left, we must extend I to include everything
// seen so far — one pass with two running maxima gives the cut in O(n), O(1) space."
//
// =============================================================================
// PROBLEM (PRECISE)
// =============================================================================
//
// Partition indices {0,…,n−1} into nonempty sets I = {0,…,k−1} and J = {k,…,n−1}
// such that:
//
//       max(nums[i] for i in I)  ≤  min(nums[j] for j in J).
//
// Return **k** = |I|, the size of the left interval (indices `0 .. k−1`). Equivalently,
// find **smallest** k ∈ {1,…,n−1} such that
//
//       L(k) = max(nums[0:k])  ≤  R(k) = min(nums[k:n])
//
// (Smallest valid **prefix length** — stop at the first split where the right side is
// no smaller than everything on the left.)
//
// =============================================================================
// APPROACH A — SUFFIX MINIMUM + PREFIX MAXIMUM (O(n) TIME, O(n) SPACE)
// =============================================================================
//
// Precompute suffix_min[i] = min(nums[i], nums[i+1], …, nums[n−1]) in one backward pass.
// Scan k = 1,…,n−1 with running left_max = max(nums[0],…,nums[k−1]):
//       if left_max ≤ suffix_min[k]: return k.
//
// Correctness: directly evaluates L(k) ≤ R(k).
//
// =============================================================================
// APPROACH B — ONE PASS, O(1) EXTRA SPACE (IMPLEMENTED BELOW)
// =============================================================================
//
// Maintain:
//   • **cur_max** — maximum value among **all** elements from index 0 through the
//     current scan position i (the "global max seen so far").
//   • **left_max** — maximum value we **require** the left block to accommodate so
//     far; initially nums[0].
//   • **cut** — candidate length |I| (answer): smallest index i such that all
//     elements before i that are **below** the current left barrier have been
//     folded into the left prefix.
//
// When we read nums[i]:
//   • Update cur_max = max(cur_max, nums[i]).
//   • If nums[i] < left_max, then nums[i] cannot stay on the right of a partition
//     whose left side only attains max = left_max — any valid partition must put
//     **this** small element in I, which forces I to include **every** position up
//     to i (otherwise something smaller than left_max would leak into J while a
//     larger value stayed in I — breaking monotonicity of the separation). The
//     editorial argument collapses to: we must extend the required left prefix to
//     index i, and the new worst-case max on the left becomes **cur_max** (everything
//     seen). Set left_max ← cur_max, cut ← i + 1.
//
// If nums[i] ≥ left_max, the element can legally live on the right; no extension.
//
// Return **cut** after the loop.
//
// This simulates finding the **minimum** k with L(k) ≤ R(k) without storing the full
// suffix table.
//
// =============================================================================
// WHY NOT BINARY SEARCH ON k?
// =============================================================================
//
// The predicate L(k) ≤ R(k) is **not** monotone in k in general (counterexamples
// exist), so binary search on k is unsafe without extra structure. Linear scan with
// the invariant above is standard.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// **Scalars only** — no arrays besides the input. Optional Approach A uses O(n)
// `suffix_min`; Approach B is **O(1)** auxiliary variables (best for memory budget).
//
// =============================================================================
// TIME & SPACE COMPLEXITY
// =============================================================================
//
// • Time: **O(n)** — single left-to-right pass (Approach A: two passes, still O(n)).
// • Space: **O(1)** extra for Approach B; **O(n)** for suffix array variant.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// • **n == 2** — only k=1 possible; algorithm returns 1.
// • **Strictly increasing** — often cut after first element if nums[0] ≤ min(rest).
// • **All equal** — any split works; algorithm returns **1** (minimum |I|).
// • **Duplicate values** — comparisons are ≤ / ≥ on integers; ties handled naturally.
//
// =============================================================================
// TESTS (SAMPLES + REGRESSION)
// =============================================================================
//
// • [5,0,3,8,6] → **3** (left [5,0,3], right [8,6]; max 5 ≤ min 6).
// • [1,1,1,0,6,12] → **4**.
// • [1,2] → **1** if 1 ≤ 2.
//
// Brute force for small n: all k from 1 to n−1, compute max/min ranges — O(n²) check.
//
// =============================================================================
// IMPROVEMENTS / VARIANTS
// =============================================================================
//
// • **Suffix min precomputation** can be easier to explain in some interviews than
//   the O(1)-space trick — trade memory for clarity.
// • **Segment trees** are overkill here.
//
// =============================================================================

// @lc code=start

// PartitionDisjoint915 returns minimum size k of a nonempty prefix such that max(prefix) <= min(suffix).
//
// Greedy one-pass: extend the mandatory prefix whenever the current value is
// still smaller than the strongest left-side maximum we have committed to.
func PartitionDisjoint915(nums []int) int {
	leftMax := nums[0]
	curMax := nums[0]
	cut := 1

	for i := 1; i < len(nums); i++ {
		if nums[i] > curMax {
			curMax = nums[i]
		}
		if nums[i] < leftMax {
			leftMax = curMax
			cut = i + 1
		}
	}

	return cut
}

// Alternative — two-pass suffix minimum (same asymptotics, O(n) extra space):
//
//     n := len(nums)
//     suf := make([]int, n)
//     suf[n-1] = nums[n-1]
//     for i := n - 2; i >= 0; i-- {
//         if nums[i] < suf[i+1] {
//             suf[i] = nums[i]
//         } else {
//             suf[i] = suf[i+1]
//         }
//     }
//     leftMax := nums[0]
//     for k := 1; k < n; k++ {
//         if leftMax <= suf[k] {
//             return k
//         }
//         if nums[k] > leftMax {
//             leftMax = nums[k]
//         }
//     }

// @lc code=end
