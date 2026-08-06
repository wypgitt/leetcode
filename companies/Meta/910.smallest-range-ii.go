package leetcode

//
// @lc app=leetcode id=910 lang=golang
//
// [910] Smallest Range II
//

// =============================================================================
// INTERVIEW: ELEVATOR PITCH (~30 seconds)
// =============================================================================
//
// "Each number can independently become either x+k or x−k. After sorting, an optimal
// assignment never mixes +k and −k arbitrarily in the middle of the order — there is
// a **cut**: every element **up to some index** gets +k (lift the low side), everything
// **after** gets −k (pull the high side down). Try each cut in O(n), tracking only the
// resulting min and max in closed form — total after sort O(n log n)."
//
// =============================================================================
// PROBLEM (PRECISE)
// =============================================================================
//
// Given integer array `nums` and integer `k ≥ 0`, replace each `nums[i]` by either
// `nums[i] + k` or `nums[i] − k` (your choice per index). Minimize
//
//       max(transformed) − min(transformed).
//
// =============================================================================
// WHY SORT FIRST — STRUCTURE OF AN OPTIMAL ASSIGNMENT
// =============================================================================
//
// Sort `A = sorted(nums)`. Label indices `0 … n−1` from smallest to largest **original**
// values.
//
// **Claim (standard for this problem):** There exists an optimal solution and a split
// index `i ∈ {−1,…,n−2}` such that:
//
//   • indices `0 … i` all use **+k**,
//   • indices `i+1 … n−1` all use **−k**.
//
// Intuition: To shrink the spread you **raise** small numbers and **lower** large ones.
// If `A[a] < A[b]` but you assigned `A[a] − k` while assigning `A[b] + k`, swapping those
// two choices moves both values **toward each other** (the smaller goes up or stays up,
// the larger goes down), never widening the range — so a monotone assignment exists.
//
// (Formal proofs appear in editorials; interviews usually accept this exchange argument
// sketch.)
//
// =============================================================================
// FORMULAS FOR MIN / MAX AFTER A SPLIT
// =============================================================================
//
// Fix split after index `i` (left block `0..i`, right block `i+1..n−1`).
//
// • Left block values are `A[0]+k, …, A[i]+k` — strictly shift by +k. Since `A` sorted,
//   **max on left** = `A[i] + k`, **min on left** = `A[0] + k`.
//
// • Right block values are `A[i+1]−k, …, A[n−1]−k`. **Max on right** = `A[n−1] − k`,
//   **min on right** = `A[i+1] − k`.
//
// Overall **maximum** after split:
//       H(i) = max(A[i] + k,  A[n−1] − k)
//
// Overall **minimum** after split:
//       L(i) = min(A[0] + k,  A[i+1] − k)
//
// Range contribution: **R(i) = H(i) − L(i)**.
//
// =============================================================================
// WHY INITIAL ANSWER COVERS “ALL +k” AND “ALL −k”
// =============================================================================
//
// If **every** element gets `+k`, range = `(A[n−1]+k) − (A[0]+k) = A[n−1] − A[0]`.
// Same if **every** element gets `−k`. So initialize:
//
//       answer = A[n−1] − A[0]
//
// Then enumerate internal splits `i = 0 … n−2` and minimize `max(H(i)−L(i), …)`.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// **Sorted array in-place** — no heaps, prefix sums, or DP tables. Only `O(1)` scalars
// while scanning splits after sort.
//
// =============================================================================
// TIME & SPACE COMPLEXITY
// =============================================================================
//
// • Sorting: **O(n log n)** time; **O(1)** extra space if in-place sort allowed (Python’s
//   `list.sort` is in-place; Timsort may use temp buffers — still **O(n)** worst-case
//   auxiliary in theory).
// • Scan splits: **O(n)** time, **O(1)** extra variables.
//
// Overall: **O(n log n)** time, **O(1)** auxiliary aside from input rearrangement.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// • **`n == 1`** — range is always `0` (max equals min).
// • **`k == 0`** — cannot change values; answer `A[n−1] − A[0]`.
// • **All equal** — answer `0`.
//
// =============================================================================
// TESTING (UNIT / SANITY)
// =============================================================================
//
// • Example-style: `nums = [1,3,6], k = 3` → sorted `[1,3,6]`; try splits; expect **3**.
// • Brute force for tiny `n`: each of `2^n` assignments — compare to `O(n)` formula on
//   sorted array for random small tests.
//
// =============================================================================
// IMPROVEMENTS / VARIANTS
// =============================================================================
//
// • No asymptotic improvement known that beats sorting for this reduction (must order
//   candidates for split enumeration).
// • If `nums` already sorted by caller, skip sort → **O(n)** scan only.
//
// =============================================================================

// @lc code=start

import "sort"

// SmallestRangeII910 minimizes (max - min) after replacing each nums[i] with nums[i]+k or nums[i]-k.
//
// Sort, then try every split: prefix +k, suffix -k; range =
//
//	max(A[i]+k, A[-1]-k) - min(A[0]+k, A[i+1]-k).
func SmallestRangeII910(nums []int, k int) int {
	a := append([]int(nil), nums...)
	sort.Ints(a)
	n := len(a)
	if n == 1 {
		return 0
	}

	best := a[n-1] - a[0]

	for i := 0; i < n-1; i++ {
		high := max910(a[i]+k, a[n-1]-k)
		low := min910(a[0]+k, a[i+1]-k)
		best = min910(best, high-low)
	}

	return best
}

func max910(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func min910(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// @lc code=end
