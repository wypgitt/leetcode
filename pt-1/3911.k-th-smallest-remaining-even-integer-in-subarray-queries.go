package leetcode

//
// @lc app=leetcode id=3911 lang=golang
//
// [3911] K-th Smallest Remaining Even Integer in Subarray Queries
//

// --- Notes (problem restatement, math, algorithm, complexity, interview flow) ---
//
// Problem restatement
// nums is strictly increasing. For each query [l, r, k]:
//   - Look at the VALUES in nums[l..r] (contiguous subarray by index).
//   - Start from the infinite sequence of positive even integers: 2, 4, 6, 8, ...
//   - Remove every even integer that appears as a value in nums[l..r].
//     (Odd values in the subarray are not in the even sequence, so they do nothing.)
//   - Among what remains, return the k-th smallest (1-indexed).
// Return one answer per query.
//
// Why not simulate removals?
// k and value ranges go up to 1e9; the answer index can be huge. We cannot iterate
// evens one by one. We need a counting / monotonic characterization and binary search.
//
// Key observation (counting formulation)
// Let Z(t) = number of positive even integers x with x <= t.
//   Z(t) = floor(t/2)  (evens 2, 4, ..., 2*floor(t/2)).
// Let R_{l,r}(t) = count of x in nums[l..r] such that x is even and x <= t.
// Then rem(t) = Z(t) - R_{l,r}(t) = how many remaining evens are <= t.
// rem(t) is non-decreasing in t (standard lower-bound setup).
// We want the smallest integer t such that rem(t) >= k  (classic "k-th = lower bound").
//
// Why rem(t) is monotone
// As t increases, the set of positive evens <= t only grows, and the set of removed
// values in nums[l..r] that are also <= t only grows. So the count of remaining evens
// with value <= t never decreases.
//
// Data structures
// - nums is sorted -> binary search (bisect) on values for "last index with nums[i] <= t".
// - Prefix sum of "is even" over nums: even_prefix[i] = #evens in nums[0..i-1].
//   Then #evens in nums[l..p] = even_prefix[p+1] - even_prefix[l] in O(1).
// No segment tree needed: each query only touches one index range in nums via bisect.
//
// Per-query steps
// 1) Define removed_evens_upto(l, r, t):
//    p = last index in nums with nums[p] <= t  (bisect_right(nums, t) - 1).
//    Clamp p into [l, r]; if no index in [l,r] has nums[i] <= t, removed count is 0.
//    Count evens in nums[l..p] using even_prefix.
// 2) rem(t) = t // 2 - removed_evens_upto(l, r, t).
// 3) Binary search smallest t in [2, hi] with rem(t) >= k.
//
// Upper bound hi for binary search
// Without removals, the k-th positive even is 2k. Each removed even in the subarray
// can force us to take a larger t (at most as bad as skipping one extra even per removal).
// Safe choice: hi = 2 * (k + n) where n = len(nums). With n <= 1e5 and k <= 1e9,
// hi fits easily in Python int.
//
// Time complexity
// Let Q = number of queries, n = len(nums).
// Per query: O(log hi * log n) for binary search on t times bisect on nums.
// log hi ~ log(k + n) ~ O(log max(k, n)). Total O(Q * log(k+n) * log n).
//
// Space complexity
// O(n) for even_prefix and the input copy; O(1) extra per query besides output array.
//
// Edge cases (sanity checks)
// - Subarray has no evens: R(t)=0 for all t -> answer is the k-th even overall = 2k.
// - Subarray removes small evens only: rem(t) catches up later (e.g. remove 4 -> 1st
//   remaining is still 2 if 2 not removed).
// - l == r, single element odd -> no removal from evens.
// - k = 1: smallest remaining even is first t with rem(t) >= 1.
// - Large k: handled by hi = 2*(k+n).
//
// Possible improvements / variants
// - Tighter hi (e.g. exponential lift first) saves a few iterations; rarely needed.
// - If queries were offline with Mo's algorithm style, might reorder for cache — here
//   queries are independent; bisect + prefix is the intended solution.
// - "Double binary search" narrative: outer BS on answer t, inner BS (bisect) on nums
//   to count removals <= t.
//
// How to explain in an interview
// 1) Reformulate "k-th remaining" as smallest t with (#evens <= t) - (#removed evens
//    in range that are <= t) >= k.
// 2) Note monotonicity -> binary search on t.
// 3) Use sorted nums + bisect + prefix counts for removed evens in O(log n).
// 4) State bounds and complexity.
// --- end notes ---

// @lc code=start

import "sort"

// KthRemainingInteger3911 answers each query on the strictly increasing nums slice.
func KthRemainingInteger3911(nums []int, queries [][]int) []int {
	n := len(nums)
	evenPrefix := make([]int, n+1)
	for i := 0; i < n; i++ {
		evenPrefix[i+1] = evenPrefix[i]
		if nums[i]%2 == 0 {
			evenPrefix[i+1]++
		}
	}

	removedEvensUpto := func(l, r, t int) int {
		p := sort.SearchInts(nums, t+1) - 1
		if p < l {
			return 0
		}
		if p > r {
			p = r
		}
		return evenPrefix[p+1] - evenPrefix[l]
	}

	kthForQuery := func(l, r, k int) int {
		hi := 2 * (k + n)
		lo := 2
		for lo < hi {
			mid := (lo + hi) / 2
			rem := mid/2 - removedEvensUpto(l, r, mid)
			if rem >= k {
				hi = mid
			} else {
				lo = mid + 1
			}
		}
		return lo
	}

	out := make([]int, len(queries))
	for i, q := range queries {
		out[i] = kthForQuery(q[0], q[1], q[2])
	}
	return out
}

// @lc code=end
