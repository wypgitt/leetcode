package leetcode

//
// @lc app=leetcode id=3850 lang=golang
//
// [3850] Count Sequences to K
//
// Notes
// Factor k and each number only over primes 2, 3, and 5. Each number may be
// skipped, added, or subtracted in exponent-vector space, so a sparse DP map
// keyed by the three exponents counts ways to reach every vector. If k has any
// other prime factor, no sequence can reach it. Time: O(n*S), where S is the
// number of reachable exponent states. Space: O(S).
//
// @lc code=start

type state3850 struct {
	a int
	b int
	c int
}

func CountSequences3850(nums []int, k int) int {
	target, reachable := factorTarget3850(k)
	if !reachable {
		return 0
	}

	dp := map[state3850]int{{}: 1}
	for _, num := range nums {
		delta := factorSmall3850(num)
		next := map[state3850]int{}
		for state, ways := range dp {
			next[state] += ways
			next[state3850{state.a + delta.a, state.b + delta.b, state.c + delta.c}] += ways
			next[state3850{state.a - delta.a, state.b - delta.b, state.c - delta.c}] += ways
		}
		dp = next
	}

	return dp[target]
}

func factorTarget3850(value int) (state3850, bool) {
	exponents := [3]int{}
	for i, prime := range []int{2, 3, 5} {
		for value%prime == 0 {
			value /= prime
			exponents[i]++
		}
	}
	return state3850{a: exponents[0], b: exponents[1], c: exponents[2]}, value == 1
}

func factorSmall3850(value int) state3850 {
	exponents := [3]int{}
	for i, prime := range []int{2, 3, 5} {
		for value%prime == 0 {
			value /= prime
			exponents[i]++
		}
	}
	return state3850{a: exponents[0], b: exponents[1], c: exponents[2]}
}

// @lc code=end
