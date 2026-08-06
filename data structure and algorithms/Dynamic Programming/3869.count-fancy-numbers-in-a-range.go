package leetcode

//
// @lc app=leetcode id=3869 lang=golang
//
// [3869] Count Fancy Numbers in a Range
//

// --- Notes (definitions, digit-sum check shortcut, digit DP, complexity, interview) ---
//
// Definitions
// GOOD integer: decimal digits are STRICTLY increasing OR STRICTLY decreasing (single-digit
// counts as good). Example: 10 is good (1>0); 11 is not (equal digits).
// FANCY integer: GOOD, OR the SUM OF DIGITS (once, no recursion in statement) is good.
// Count fancy numbers in [l, r] inclusive.
//
// Range answer trick
// Let F(x) = count of fancy numbers in [0, x]. Answer = F(r) - F(l - 1).
//
// check(s) — is nonnegative integer s "good" as a decimal number?
// Used when the full number is NOT good (strict monotonicity broken, state st == 3) but we
// still need to know if DIGIT SUM s is good to mark fancy.
// - For s < 100: two-digit "bad" pattern is repeated digits 11, 22, ..., 99, i.e. multiples of
//   11 with two digits (and 0). Single digits pass. So s % 11 != 0 matches the editorial test.
// - For s >= 100: digit sums coming from up to 16 nines are bounded (~144); the solution uses
//   the simplified predicate in the statement code: strict increase on the last two decimal
//   digits of s (contest algebra); keep the same logic as official solutions.
//
// Digit DP state (process bound string num from high to low)
// dfs(pos, s, prev, st, lim):
//   pos   — index in num.
//   s     — running digit sum of the number being built.
//   prev  — previous digit placed (0 for leading-zero phase).
//   st    — monotonicity of the decimal string so far:
//           0 = only leading zeros / compatible prefix (see transitions),
//           1 = strict increase chain,
//           2 = strict decrease chain,
//           3 = already impossible to be strictly monotone.
//   lim   — tight to upper bound num (standard digit DP).
// Terminal: if st != 3, the number itself is good -> count 1. If st == 3, fancy iff check(s).
//
// Leading zeros: prev == 0 and st == 0 allow leading zeros until first nonzero digit; transitions
// match the official implementation.
//
// Caching: memo cleared when switching bound string (l-1 vs r) because num changes.
//
// Time complexity
// O(states * 10) per bound with memo; digit positions O(log10 r), sum s up to 9 * digits,
// prev in 0..9, st in 0..3 — polynomial in digit count; effectively ~O(D * S * 10) with small D.
//
// Space complexity
// Memo table proportional to reachable states for one bound.
//
// Edge cases
// l = 1: use F(r) - F(0). String "0" works with DP for zero.
// Single-element range: still two F evaluations.
//
// Tests (examples)
// [8,10] -> 3; [12340,12341] -> 1; singleton non-fancy -> 0.
//
// Possible improvements
// - Iterative DP table instead of recursion; same states.
// - Explicit memo dimensions instead of cache_clear if you pass num as tuple key (larger memory).
// --- end notes ---

// @lc code=start

import "strconv"

type key3869 struct {
	pos, s, prev, st int
	lim               bool
}

func check3869(s int) bool {
	if s < 100 {
		return s%11 != 0
	}
	return 1 < (s/10)%10 && (s/10)%10 < s%10
}

// CountFancy3869 counts fancy integers in [l, r] inclusive.
func CountFancy3869(l, r int) int {
	calc := func(x int) int {
		num := strconv.Itoa(x)
		memo := make(map[key3869]int)
		var dfs func(pos, s, prev, st int, lim bool) int
		dfs = func(pos, s, prev, st int, lim bool) int {
			k := key3869{pos, s, prev, st, lim}
			if v, ok := memo[k]; ok {
				return v
			}
			if pos >= len(num) {
				if st != 3 {
					memo[k] = 1
					return 1
				}
				v := 0
				if check3869(s) {
					v = 1
				}
				memo[k] = v
				return v
			}
			up := 9
			if lim {
				up = int(num[pos] - '0')
			}
			res := 0
			for i := 0; i <= up; i++ {
				nxtSt := st
				if st == 0 {
					if prev == 0 {
						nxtSt = 0
					} else if i > prev {
						nxtSt = 1
					} else if i < prev {
						nxtSt = 2
					} else {
						nxtSt = 3
					}
				} else if st == 1 {
					if i > prev {
						nxtSt = 1
					} else {
						nxtSt = 3
					}
				} else if st == 2 {
					if i < prev {
						nxtSt = 2
					} else {
						nxtSt = 3
					}
				} else {
					nxtSt = 3
				}
				nextLim := lim && i == up
				res += dfs(pos+1, s+i, i, nxtSt, nextLim)
			}
			memo[k] = res
			return res
		}
		return dfs(0, 0, 0, 0, true)
	}
	return calc(r) - calc(l-1)
}

// @lc code=end
