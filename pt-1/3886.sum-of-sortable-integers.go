package leetcode

//
// @lc app=leetcode id=3886 lang=golang
//
// [3886] Sum of Sortable Integers
//

// --- Notes (problem restatement, characterization, algorithm, complexity, interview) ---
//
// Problem restatement
// nums length n. Integer k (positive divisor of n) is SORTABLE iff we can reach the fully
// NON-DECREASING arrangement of nums by:
//   1) Split nums into consecutive blocks of length k (exactly n/k blocks).
//   2) Inside EACH block, apply cyclic rotations (left/right any number of times) —
//      only orders reachable from the original block order are cyclic shifts.
// Sum EVERY divisor k of n for which k is sortable; return that sum.
//
// Characterization of sortability for fixed k
// Let S = sorted(nums) (global target order). For concatenated blocks to equal S, block i
// (0-indexed) MUST realize exactly S[i*k : (i+1)*k] as values in order — those are the k
// multiset positions in the sorted array for that segment.
// So for each block:
//   (a) Multiset(block_i from nums) = multiset(S[i*k : (i+1)*k]).
//   (b) The physical block in nums must be a CYCLIC ROTATION of the target segment S[i*k:(i+1)*k]
//       as sequences (same length, same multiset, one is a rotate of the other).
// If (a) fails, wrong multiset — impossible. If (a) holds but (b) fails, we cannot rotate the
// original trace into the sorted segment order — impossible.
// If both hold for every block, k is sortable.
//
// Special cases
// - k = n: one block; sortable iff nums is a cyclic rotation of sorted(nums) — e.g. [3,1,2]
//   works because it rotates to [1,2,3].
// - k = 1: each block is one element; rotation does nothing. Sortable iff nums is ALREADY
//   sorted (each position must match S).
// - nums already sorted: every divisor k works (use identity rotation per block) — Example 3.
//
// Checking cyclic rotation in O(k) — important for performance
// Compare multisets (Counter or sorted(block) vs seg). Segment seg = S[i:i+k] is already
// non-decreasing, so multiset equality is Counter(block)==Counter(seg) in O(k), or
// sorted(block)==seg without sorting seg.
// Rotation: block must occur as a length-k window in (seg + seg). A naive scan over k start
// offsets with full slice compare is O(k^2) per block and TIME LIMITS on large n (e.g. k ~ n/2).
// Use KMP substring search on integer arrays: O(k) per block.
//
// Why enumerate divisors of n
// k must divide n so that integer-length blocks tile the array; only those k are candidates.
//
// Algorithm
//   S = sorted(nums)
//   ans = 0
//   for each divisor k of n:
//       if all blocks pass multiset + rotation checks: ans += k
//   return ans
//
// Time complexity
// Let tau(n) be the number of divisors of n (for n <= 1e5, tau(n) is small, ~128 worst-ish).
// For each divisor, sum over blocks of O(k) multiset + O(k) KMP = O(n) per divisor.
// Overall O(n * tau(n)); avoid O(k^2) rotation naive scan.
//
// Space complexity
// O(n) for sorted copy and temporary doubled segment seg+seg (length 2k per block worst O(n)
// for single block).
//
// Possible improvements
// - Double rolling hash instead of KMP (same O(k); watch collisions).
// - For multiset only, sorted(block)==seg when seg is sorted — still O(k log k); Counter is O(k).
//
// Edge cases
// - All equal values: any rotation works; sorted equals nums pattern — typically all k pass if
//   multisets align per block (they will).
// - n prime: divisors 1 and n only.
//
// Interview walkthrough
// 1) Observe global sorted target S fixes each block's multiset and order segment S[i*k:...].
// 2) Independent cyclic rotations per block -> each block must be a rotation of that segment.
// 3) Implement divisor enumeration + O(n) validation per k.
// 4) Argue O(n * tau(n)) time.
// --- end notes ---

// @lc code=start

import "sort"

// SortableIntegers3886 returns sum of divisors k of n for which nums is k-sortable.
func SortableIntegers3886(nums []int) int {
	n := len(nums)
	s := append([]int(nil), nums...)
	sort.Ints(s)

	divs := divisors3886(n)
	ans := 0
	for _, k := range divs {
		if ok3886(nums, s, n, k) {
			ans += k
		}
	}
	return ans
}

func divisors3886(x int) []int {
	var out []int
	for i := 1; i*i <= x; i++ {
		if x%i == 0 {
			out = append(out, i)
			if i*i != x {
				out = append(out, x/i)
			}
		}
	}
	return out
}

func counterEq3886(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	m := make(map[int]int, len(a))
	for _, x := range a {
		m[x]++
	}
	for _, x := range b {
		m[x]--
		if m[x] == 0 {
			delete(m, x)
		}
	}
	return len(m) == 0
}

func kmpContains3886(pat, txt []int) bool {
	if len(pat) == 0 {
		return true
	}
	m, ln := len(pat), len(txt)
	if m > ln {
		return false
	}
	lps := make([]int, m)
	length := 0
	for i := 1; i < m; {
		if pat[i] == pat[length] {
			length++
			lps[i] = length
			i++
		} else if length > 0 {
			length = lps[length-1]
		} else {
			lps[i] = 0
			i++
		}
	}
	j := 0
	for i := 0; i < ln; {
		if txt[i] == pat[j] {
			i++
			j++
			if j == m {
				return true
			}
		} else if j > 0 {
			j = lps[j-1]
		} else {
			i++
		}
	}
	return false
}

func ok3886(nums, s []int, n, k int) bool {
	for i := 0; i < n; i += k {
		block := nums[i : i+k]
		seg := s[i : i+k]
		if !counterEq3886(block, seg) {
			return false
		}
		dbl := append(append([]int(nil), seg...), seg...)
		if !kmpContains3886(block, dbl) {
			return false
		}
	}
	return true
}

// @lc code=end
