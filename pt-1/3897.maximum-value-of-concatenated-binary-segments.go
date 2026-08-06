//
// @lc app=leetcode id=3897 lang=python3
//
// [3897] Maximum Value of Concatenated Binary Segments
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
// @lc app=leetcode id=3897 lang=python3
//
// [3897] Maximum Value of Concatenated Binary Segments
//
// --- Notes (problem restatement, greedy sort, value accumulation, complexity) ---
//
// Problem restatement
// Two arrays nums1, nums0 of length n. Segment i is the binary string:
//   ones^(nums1[i]) followed by zeros^(nums0[i])   i.e. "11..100..0"
// You may permute the n segments in any order, then concatenate them into one binary
// string (no separator). Maximize the INTEGER value of that binary number.
// Return answer modulo 1_000_000_007.
//
// Same-length binary comparison
// For two binary strings of EQUAL length, numeric compare equals LEXICOGRAPHIC compare
// (both compare MSB first). Here total length m is fixed for any permutation (sum of
// all segment lengths), so maximizing value equals maximizing lex order as a string.
//
// Greedy structure (three kinds of segments)
// Write segment as S(x,y) = 1^x 0^y with x = nums1[i], y = nums0[i].
// - Type A (y = 0): only ones — pushing these left puts weight on higher bits without
//   inserting zeros early. Among type-A blocks, more ones first (compare two all-one
//   strings of different lengths).
// - Type B (x > 0 and y > 0): has both runs — earlier segments matter most; putting a
//   block with more leading 1s earlier dominates; tie-break with FEWER trailing zeros
//   so we delay switching to the low-value tail.
// - Type C (x = 0 and y > 0): only zeros — must sit at the RIGHT end (they contribute no
//   1 bits but occupy higher positions if placed early). Among zero-only blocks, shorter
//   first frees positions... Official sort uses ascending y among type-C (see comparator).
//
// Comparator implemented as sort key (three-tier groups + ties)
// Group 0: y == 0   -> key (0, -x, 0)   => larger x first among pure-one segments.
// Group 1: x > 0 and y > 0 -> (1, -x, y) => larger x first; if tie on x, smaller y first.
// Group 2: x == 0   -> key (2, y, 0)    => pure-zero segments last; ascending y among them.
// Ordering: group 0 < group 1 < group 2 so pure-one blocks come first, pure-zero last.
//
// Pairwise intuition (why local order matches global optimum)
// Compare concatenating A=S(a,b) vs B=S(c,d). Checking AB vs BA lexicographically gives
// the same tie-breaking encoded above; sorting by this comparator yields optimal global
// order for concatenation problems where comparison is "consistent" (standard exchange
// argument / greedy reorder for multiset of strings under lex-max concatenation with a
// suitable comparator — contest reduction packages this into the three-type rule).
//
// Computing value without building the bit string
// Let total length m = sum(nums1) + sum(nums0). Precompute pow2[k] = 2^k mod MOD for
// k = 0..m-1. Scan segments in sorted order. Maintain bit-index `pos` from the MSB:
// each '1' adds pow2[pos]; each position consumed moves toward less significant bits by
// decrementing pos. Equivalently: start pos = m-1; for each '1' add pow2[pos]; pos--; for
// each '0' only pos -= (zeros consume significance slots without adding to the sum).
//
// Modular arithmetic
// All additions use MOD = 10**9 + 7; pow2 built iteratively (p[i] = (p[i-1]*2) % MOD).
//
// Time complexity
// O(n log n + m) — sort n segments; O(m) to fill powers and simulate placing bits.
// With m <= 2*10^5 from constraints, this is fine.
//
// Space complexity
// O(n + m) for pairs and the power table (m up to 2*10^5).
//
// Edge cases
// - n = 1: sort is trivial; single segment value is (binary value of 1^x 0^y).
// - y = 0 for all: all type A; order by x descending — all ones string, value 2^m - 1 in
//   integer terms (mod applied).
// - x = 0 for a segment: that segment is zeros only; it will be in group 2 at the end.
// - nums1[i] + nums0[i] > 0: no empty segment.
//
// Possible improvements
// - On-the-fly power: keep running "current weight" w = 2^{pos} mod MOD and update
//   w = w * inv(2) mod MOD when moving right — needs modular inverse of 2; precompute
//   pow2 is simpler and O(m) anyway.
// - For very large m one could use repeated squaring, but m is only 2e5 here.
//
// Interview walkthrough
// 1) Fixed total length => maximize lex order of bit string.
// 2) Classify segments; sort with the 3-type rule and tie-breaks.
// 3) Accumulate value with power-of-two weights from MSB to LSB without materializing
//    the string.
// 4) State O(n log n + m) time, O(n + m) space, modulo.
// --- end notes ---
//
// @lc code=start
// class Solution:
//     def maxValue(self, nums1: list[int], nums0: list[int]) -> int:
//         MOD = 10**9 + 7
//         pairs = list(zip(nums1, nums0))
//         b = sum(x + y for x, y in pairs)
//
//         def key(p: tuple[int, int]) -> tuple[int, int, int]:
//             x, y = p
//             if y == 0:
//                 return (0, -x, 0)
//             if x > 0:
//                 return (1, -x, y)
//             return (2, y, 0)
//
//         pairs.sort(key=key)
//
//         ans = 0
//         pow2 = [1] * b
//         for i in range(1, b):
//             pow2[i] = pow2[i - 1] * 2 % MOD
//
//         b -= 1
//         for cnt1, cnt0 in pairs:
//             while cnt1:
//                 ans = (ans + pow2[b]) % MOD
//                 b -= 1
//                 cnt1 -= 1
//             b -= cnt0
//         return ans
//
//
// @lc code=end
//
package leetcode

//
// @lc app=leetcode id=3897 lang=golang
//
// [3897] Maximum Value of Concatenated Binary Segments
//

// --- Notes (problem restatement, greedy sort, value accumulation, complexity) ---
//
// Problem restatement
// Two arrays nums1, nums0 of length n. Segment i is the binary string:
//   ones^(nums1[i]) followed by zeros^(nums0[i])   i.e. "11..100..0"
// You may permute the n segments in any order, then concatenate them into one binary
// string (no separator). Maximize the INTEGER value of that binary number.
// Return answer modulo 1_000_000_007.
//
// Same-length binary comparison
// For two binary strings of EQUAL length, numeric compare equals LEXICOGRAPHIC compare
// (both compare MSB first). Here total length m is fixed for any permutation (sum of
// all segment lengths), so maximizing value equals maximizing lex order as a string.
//
// Greedy structure (three kinds of segments)
// Write segment as S(x,y) = 1^x 0^y with x = nums1[i], y = nums0[i].
// - Type A (y = 0): only ones — pushing these left puts weight on higher bits without
//   inserting zeros early. Among type-A blocks, more ones first (compare two all-one
//   strings of different lengths).
// - Type B (x > 0 and y > 0): has both runs — earlier segments matter most; putting a
//   block with more leading 1s earlier dominates; tie-break with FEWER trailing zeros
//   so we delay switching to the low-value tail.
// - Type C (x = 0 and y > 0): only zeros — must sit at the RIGHT end (they contribute no
//   1 bits but occupy higher positions if placed early). Among zero-only blocks, shorter
//   first frees positions... Official sort uses ascending y among type-C (see comparator).
//
// Comparator implemented as sort key (three-tier groups + ties)
// Group 0: y == 0   -> key (0, -x, 0)   => larger x first among pure-one segments.
// Group 1: x > 0 and y > 0 -> (1, -x, y) => larger x first; if tie on x, smaller y first.
// Group 2: x == 0   -> key (2, y, 0)    => pure-zero segments last; ascending y among them.
// Ordering: group 0 < group 1 < group 2 so pure-one blocks come first, pure-zero last.
//
// Pairwise intuition (why local order matches global optimum)
// Compare concatenating A=S(a,b) vs B=S(c,d). Checking AB vs BA lexicographically gives
// the same tie-breaking encoded above; sorting by this comparator yields optimal global
// order for concatenation problems where comparison is "consistent" (standard exchange
// argument / greedy reorder for multiset of strings under lex-max concatenation with a
// suitable comparator — contest reduction packages this into the three-type rule).
//
// Computing value without building the bit string
// Let total length m = sum(nums1) + sum(nums0). Precompute pow2[k] = 2^k mod MOD for
// k = 0..m-1. Scan segments in sorted order. Maintain bit-index `pos` from the MSB:
// each '1' adds pow2[pos]; each position consumed moves toward less significant bits by
// decrementing pos. Equivalently: start pos = m-1; for each '1' add pow2[pos]; pos--; for
// each '0' only pos -= (zeros consume significance slots without adding to the sum).
//
// Modular arithmetic
// All additions use MOD = 10**9 + 7; pow2 built iteratively (p[i] = (p[i-1]*2) % MOD).
//
// Time complexity
// O(n log n + m) — sort n segments; O(m) to fill powers and simulate placing bits.
// With m <= 2*10^5 from constraints, this is fine.
//
// Space complexity
// O(n + m) for pairs and the power table (m up to 2*10^5).
//
// Edge cases
// - n = 1: sort is trivial; single segment value is (binary value of 1^x 0^y).
// - y = 0 for all: all type A; order by x descending — all ones string, value 2^m - 1 in
//   integer terms (mod applied).
// - x = 0 for a segment: that segment is zeros only; it will be in group 2 at the end.
// - nums1[i] + nums0[i] > 0: no empty segment.
//
// Possible improvements
// - On-the-fly power: keep running "current weight" w = 2^{pos} mod MOD and update
//   w = w * inv(2) mod MOD when moving right — needs modular inverse of 2; precompute
//   pow2 is simpler and O(m) anyway.
// - For very large m one could use repeated squaring, but m is only 2e5 here.
//
// Interview walkthrough
// 1) Fixed total length => maximize lex order of bit string.
// 2) Classify segments; sort with the 3-type rule and tie-breaks.
// 3) Accumulate value with power-of-two weights from MSB to LSB without materializing
//    the string.
// 4) State O(n log n + m) time, O(n + m) space, modulo.
// --- end notes ---

// @lc code=start

import "sort"

const mod3897 = 1_000_000_007

type pair3897 struct {
	x, y int
	key  [3]int
}

// MaxValue3897 returns maximum concatenated binary value modulo 1e9+7.
func MaxValue3897(nums1, nums0 []int) int {
	n := len(nums1)
	pairs := make([]pair3897, n)
	sum := 0
	for i := 0; i < n; i++ {
		x, y := nums1[i], nums0[i]
		sum += x + y
		var k [3]int
		if y == 0 {
			k = [3]int{0, -x, 0}
		} else if x > 0 {
			k = [3]int{1, -x, y}
		} else {
			k = [3]int{2, y, 0}
		}
		pairs[i] = pair3897{x: x, y: y, key: k}
	}

	sort.Slice(pairs, func(i, j int) bool {
		a, b := pairs[i].key, pairs[j].key
		if a[0] != b[0] {
			return a[0] < b[0]
		}
		if a[1] != b[1] {
			return a[1] < b[1]
		}
		return a[2] < b[2]
	})

	pow2 := make([]int, sum)
	pow2[0] = 1
	for i := 1; i < sum; i++ {
		pow2[i] = pow2[i-1] * 2 % mod3897
	}

	ans := 0
	b := sum - 1
	for _, p := range pairs {
		cnt1, cnt0 := p.x, p.y
		for cnt1 > 0 {
			ans = (ans + pow2[b]) % mod3897
			b--
			cnt1--
		}
		b -= cnt0
	}
	return ans
}

// @lc code=end
