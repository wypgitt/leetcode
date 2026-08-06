package leetcode

//
// @lc app=leetcode id=2719 lang=golang
//
// [2719] Count of Integers
//
// --- Interview notes (range reduction, digit DP, state, complexity, edges, tests) ---
//
// Problem
// Count integers x with num1 <= x <= num2 (given as decimal strings) such that
//   min_sum <= digit_sum(x) <= max_sum.
// Return the count modulo 1_000_000_007.
//
// Range reduction (inclusion–exclusion on the upper bound)
// Let F(N) = # of integers x with 0 <= x <= N and digit sum in [min_sum, max_sum].
// Then answer = F(num2) - F(num1 - 1)  (all with the same [min_sum, max_sum] filter).
// Reason: {x : num1 <= x <= num2} = {x : 0 <= x <= num2} \ {x : 0 <= x <= num1-1}.
// Compute num1 - 1 as a string (big-integer style borrow) so we never convert the full range to int
// (though Python int would work for |num| <= 1e22, string arithmetic matches interview expectations).
//
// Digit DP for F(N)
// Process the decimal string of N from most significant to least, with:
//   pos  — current index in the string
//   s    — sum of digits fixed so far
//   limit— if True, the prefix so far matches N[0:pos] so the next digit is at most N[pos];
//          if False, the number is already strictly below N, so the next digit can be 0..9.
// Transition: try each digit d in 0..up (up = N[pos] if limit else 9), add d to s, propagate limit' = limit and d==N[pos].
// Base: at pos == len(N), return 1 if min_sum <= s <= max_sum else 0.
// Leading zeros are allowed, so this counts all x in [0, N] with correct digit sums (shorter numbers correspond to
// prefixes of zeros, which matches standard “leading zero” digit DP).
//
// Memoization
// Only states with limit=False can be memoized across branches sharing suffix freedom — equivalent to caching all
// (pos, s, limit); with len(N) <= 23 and s <= 200-ish (23 * 9), state space is tiny.
//
// Why not iterate x from num1 to num2
// Range width can be ~1e22 — impossible.
//
// Time complexity
// O(len · max_sum_state · 10) per F(N); two calls → O(len · max_sum · 10). Here len <= ~23, digit sum in recursion
// capped by len·9 (≤ 207), well below max_sum constraint 400 for pruning discussion — effectively bounded table size.
//
// Space complexity
// O(len · max_digit_sum) for memo / recursion stack.
//
// Edge cases
// num1 == num1 (single value range): still correct via F(num2) - F(num1-1).
// num1 == "1": num1 - 1 == "0"; F counts zero (often excluded by min_sum >= 1 in constraints).
// min_sum <= digit_sum <= max_sum when min_sum > max_sum never happens per constraints.
//
// Tests (statement)
// num1="1", num2="12", min_sum=1, max_sum=8 → 11.
// num1="1", num2="5", min_sum=1, max_sum=5 → 5.
//
// Improvements
// - Prune recursion when s > max_sum (cannot end in range) to skip work — micro-optimization.
// - Iterative DP by digit position is possible; memoized DFS is standard in interviews.
//
// --- end notes ---
//
// @lc code=start

// Count2719 returns the count of integers in [num1, num2] with digit sum within [minSum, maxSum].
func Count2719(num1 string, num2 string, minSum int, maxSum int) int {
	const mod int = 1_000_000_007

	subOne := func(s string) string {
		b := []byte(s)
		i := len(b) - 1
		for i >= 0 {
			if b[i] != '0' {
				b[i]--
				break
			}
			b[i] = '9'
			i--
		}
		// strip leading zeros
		j := 0
		for j < len(b) && b[j] == '0' {
			j++
		}
		if j == len(b) {
			return "0"
		}
		return string(b[j:])
	}

	f := func(num string) int {
		digits := make([]int, len(num))
		for i := 0; i < len(num); i++ {
			digits[i] = int(num[i] - '0')
		}

		// memo[pos][sum] for limit==0, -1 means unset
		memo := make([][]int, len(num)+1)
		for i := range memo {
			memo[i] = make([]int, maxSum+1)
			for s := 0; s <= maxSum; s++ {
				memo[i][s] = -1
			}
		}

		var dfs func(pos int, sum int, limit bool) int
		dfs = func(pos int, sum int, limit bool) int {
			if pos == len(digits) {
				if minSum <= sum && sum <= maxSum {
					return 1
				}
				return 0
			}
			if sum > maxSum {
				return 0
			}
			if !limit {
				if memo[pos][sum] != -1 {
					return memo[pos][sum]
				}
			}

			up := 9
			if limit {
				up = digits[pos]
			}
			total := 0
			for d := 0; d <= up; d++ {
				if sum+d > maxSum {
					break
				}
				nxt := dfs(pos+1, sum+d, limit && d == up)
				total += nxt
				if total >= mod {
					total -= mod
				}
			}

			if !limit {
				memo[pos][sum] = total
			}
			return total
		}

		return dfs(0, 0, true)
	}

	a := f(num2)
	b := f(subOne(num1))
	res := a - b
	res %= mod
	if res < 0 {
		res += mod
	}
	return res
}

// @lc code=end

