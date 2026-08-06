package leetcode

//
// @lc app=leetcode id=2681 lang=golang
//
// [2681] Power of Heroes
//
// --- Interview notes (statement, math, algorithm, DS, complexity, edges, tests) ---
//
// Problem
// Given nums, consider every non-empty subsequence (equivalently: pick any non-empty subset of indices,
// keep order irrelevant because only min/max matter). For a chosen group G with values V,
//   power(G) = (max V)^2 * (min V).
// Return the sum of power over all non-empty groups, modulo M = 10^9 + 7.
//
// Why brute force fails
// There are O(2^n) subsequences — far too many for n ≈ 10^5.
//
// Key observation — only min and max matter
// Sort nums ascending: a[0] ≤ … ≤ a[n-1]. For any group, max is some a[j] and min is some a[i] with i ≤ j.
// Fix the maximum element to be x = a[k] (must appear in the group). Then every other chosen element
// must come from indices ≤ k; including index k forces the max to be x iff we actually include an
// occurrence of value x at position k — standard handling: sort and sweep; duplicates are fine because
// each position is distinct in subsequences.
//
// Algebraic decomposition (rigorous)
// Let F(i) = sum of min(S) over all non-empty subsets S of {a[0], …, a[i]} (values at distinct indices).
// Claim: F(i) = 2·F(i−1) + a[i].
// Proof sketch:
//   Split non-empty subsets of {a[0]…a[i]} into those not containing a[i] (sum = F(i−1)) and those
//   containing a[i]. Any subset containing a[i] is U ∪ {a[i]} with U ⊆ {a[0]…a[i−1]} (U possibly empty).
//   min(U ∪ {a[i]}) = a[i] if U is empty; otherwise min(U ∪ {a[i]}) = min(U) because the array is sorted
//   so min(U) ≤ a[i]. Summing over all U gives a[i] + sum_{non-empty U} min(U) = a[i] + F(i−1).
//   Total F(i) = F(i−1) + (a[i] + F(i−1)) = 2·F(i−1) + a[i].
//
// Contribution when max equals a[k]
// Groups whose maximum value is exactly a[k] must include at least one chosen element equal to a[k];
// when sweeping sorted order, processing element x = a[k], all “previous” elements are ≤ x.
// Sum over all U ⊆ prefix-before-x of min(U ∪ {x}) where “prefix” runs over multiset of earlier indices:
//   = x + sum_{non-empty U ⊆ earlier positions} min(U) = x + F_prev,
// where F_prev is F(k−1) if we treat prefix indices 0..k−1.
// Multiply by x^2 for power:
//   contrib(k) = x^2 · (x + F_prev) = x^3 + x^2 · F_prev.
//
// Sweep invariant
// Maintain p = F for the multiset of values already processed (all strictly earlier elements in sorted order).
// Initially p = 0 (empty prefix has no non-empty subset).
// After handling value x:
//   ans += x^3 + x^2 · p   (mod M),
//   p ← 2·p + x            (mod M), because new F = 2·old F + x.
//
// Why sort first
// Sorting guarantees that when we treat x as the maximum of a group, every element we may still add on the
// left is ≤ x, so “min(U ∪ {x}) = min(U)” for non-empty U ⊆ prefix holds — the recurrence for F is valid.
//
// Data structures
// Sort in place (or sorted copy). Only scalars ans, p — O(1) extra memory besides the array.
//
// Time complexity
// O(n log n) from sorting; O(n) scan.
//
// Space complexity
// O(1) auxiliary if sorting in place (typical sort uses O(log n) stack); O(n) for the array itself.
//
// Modular arithmetic
// Use MOD = 10^9 + 7; reduce after each multiply/add to avoid Python slowdown / match required output.
// In C++/Java, use long long and apply mod carefully on products like (x*x)%MOD * x.
//
// Edge cases
// n == 1: only group {nums[0]} → nums[0]^3.
// Duplicates: formula still holds — indices are distinct even if values repeat.
//
// Tests (sanity)
// nums = [2,1,4] → sort [1,2,4]; cumulatively ans = 141 (matches brute over all non-empty subsequences).
// nums = [1,1,1] → seven non-empty subsequences each with power 1 → ans = 7.
//
// Improvements
// None asymptotically better than sort + linear pass for this formulation; counting sort possible if
// value range were tiny (here values up to 1e9 — not applicable).
//
// --- end notes ---
//
// @lc code=start

import "sort"

// SumOfPower2681 returns the sum of (max^2 * min) over all non-empty subsequences.
func SumOfPower2681(nums []int) int {
	const MOD int64 = 1_000_000_007
	sort.Ints(nums)

	var ans int64
	var p int64 // sum of mins over all non-empty subsets of processed prefix
	for _, xv := range nums {
		x := int64(xv) % MOD
		xx := (x * x) % MOD
		ans = (ans + (xx*x)%MOD + (xx*p)%MOD) % MOD
		p = (p*2 + x) % MOD
	}
	return int(ans)
}

// @lc code=end

