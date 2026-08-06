//
// @lc app=leetcode id=3883 lang=python3
//
// [3883] Count Non-decreasing Arrays With Given Digit Sums
//
//
// @lc code=start
// class Solution:
//     pass
//
//
// @lc code=end
//
// #
// @lc app=leetcode id=3883 lang=python3
//
// [3883] Count Non Decreasing Arrays With Given Digit Sums
//
// --- Notes (problem restatement, feasibility, DP + prefix sums, complexity, interview) ---
//
// Problem restatement (from constraints)
// Given digitSum[0..n-1], count arrays arr[0..n-1] such that:
//   - Each arr[i] is an integer with 0 <= arr[i] <= 5000.
//   - arr is non-decreasing: arr[i] <= arr[i+1].
//   - Sum of decimal digits of arr[i] equals digitSum[i].
// Return count modulo 1_000_000_007.
//
// Key observations
// - digitSum[i] <= 50 (given). Only finitely many candidates exist per position once we
//   restrict arr[i] <= 5000; pre-group integers in [0, 5000] by digit-sum.
// - If some digitSum[i] admits NO integer in [0, 5000] with that digit-sum (e.g. 49),
//   answer is 0 immediately (Example 3).
//
// DP state
// Let dp_i[v] = number of valid fillings for prefix ending at position i with arr[i] = v.
// Transition (non-decreasing): arr[i] must be >= arr[i-1], so
//   dp_i[v] = sum_{u <= v} dp_{i-1}[u]   for all v allowed at position i
//            (and 0 if v is not allowed at position i).
// This is a capped suffix of the cumulative distribution of dp_{i-1}: prefix sums on v.
//
// Implementation trick (dense arrays, O(MAXV) per layer)
// MAXV = 5000. Maintain prev[v] for v = 0..MAXV (sparse mostly zero — OK memory ~5001 ints).
// Build pref[t] = sum_{u <= t} prev[u] mod MOD for t = 0..MAXV in one left-to-right scan.
// Then for each v in candidates[digitSum[i]], set cur[v] = pref[v].
//
// Initialization (i = 0)
// prev[v] = 1 for each v allowed by digitSum[0]; else 0. Exactly one way to end at each v.
//
// Answer
// sum_v prev[v] after processing last index — any ending value is allowed.
//
// Why not iterate over all pairs (u,v)
// Naive O(|V|^2) per step would be too heavy when many values share a digit-sum; prefix sums
// reduce each layer to O(MAXV + |candidates|).
//
// Time complexity
// Precompute buckets once: O(MAXV * log10 MAXV) ~ O(MAXV).
// Each of n-1 transitions: O(MAXV) for prefix + O(|bucket|) assignments — O(MAXV) per layer.
// Total O(n * MAXV) with MAXV = 5000, n <= 1000 -> ~5e6 operations.
//
// Space complexity
// O(MAXV) for prev / cur / pref arrays (plus bucket lists total size O(MAXV)).
//
// Edge cases
// - digitSum contains value with empty bucket -> 0.
// - Single element: answer is number of integers in [0,5000] with that digit-sum (Example 2).
// - arr[i]=0 has digit-sum 0; include 0 in digit-sum computation (loop-based routine returns 0).
//
// Possible improvements
// - Coordinate compression per layer (only values appearing in adjacent buckets) if MAXV grew.
// - Sparse map DP if ranges exploded — not needed here.
//
// Interview walkthrough
// 1) Bound arr[i] <= 5000 + digit-sum constraint -> finite candidate sets per index.
// 2) Non-decreasing chain -> cumulative sum over previous DP row.
// 3) Modular arithmetic end-to-end.
// --- end notes ---
//
// @lc code=start
// MOD = 10**9 + 7
// MAXV = 5000
//
//
// def _digit_sum(x: int) -> int:
//     s = 0
//     while x:
//         s += x % 10
//         x //= 10
//     return s
//
//
// _BY_SUM = [[] for _ in range(51)]
// for _x in range(MAXV + 1):
//     _BY_SUM[_digit_sum(_x)].append(_x)
//
//
// class Solution:
//     def countArrays(self, digitSum: list[int]) -> int:
//         for s in digitSum:
//             if s > 50 or not _BY_SUM[s]:
//                 return 0
//
//         prev = [0] * (MAXV + 1)
//         for v in _BY_SUM[digitSum[0]]:
//             prev[v] = 1
//
//         for i in range(1, len(digitSum)):
//             running = 0
//             pref = [0] * (MAXV + 1)
//             for t in range(MAXV + 1):
//                 running = (running + prev[t]) % MOD
//                 pref[t] = running
//             cur = [0] * (MAXV + 1)
//             for v in _BY_SUM[digitSum[i]]:
//                 cur[v] = pref[v]
//             prev = cur
//
//         return sum(prev) % MOD
//
//
// @lc code=end
//
package leetcode

const (
	mod3883  int64 = 1_000_000_007
	maxV3883       = 5000
)

var bySum3883 [51][]int

func digitSum3883(x int) int {
	s := 0
	for x > 0 {
		s += x % 10
		x /= 10
	}
	return s
}

func init() {
	for x := 0; x <= maxV3883; x++ {
		s := digitSum3883(x)
		if s <= 50 {
			bySum3883[s] = append(bySum3883[s], x)
		}
	}
}

// CountArrays3883 counts non-decreasing arrays with given digit sums.
func CountArrays3883(digitSum []int) int {
	for _, s := range digitSum {
		if s > 50 || len(bySum3883[s]) == 0 {
			return 0
		}
	}
	if len(digitSum) == 0 {
		return 0
	}

	prev := make([]int64, maxV3883+1)
	for _, v := range bySum3883[digitSum[0]] {
		prev[v] = 1
	}

	for i := 1; i < len(digitSum); i++ {
		pref := make([]int64, maxV3883+1)
		var running int64
		for t := 0; t <= maxV3883; t++ {
			running += prev[t]
			running %= mod3883
			pref[t] = running
		}
		cur := make([]int64, maxV3883+1)
		for _, v := range bySum3883[digitSum[i]] {
			cur[v] = pref[v]
		}
		prev = cur
	}

	var ans int64
	for _, v := range prev {
		ans += v
	}
	return int(ans % mod3883)
}

