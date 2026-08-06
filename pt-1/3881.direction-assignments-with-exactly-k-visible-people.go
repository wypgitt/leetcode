package leetcode

//
// @lc app=leetcode id=3881 lang=golang
//
// [3881] Direction Assignments With Exactly K Visible People
//
// Notes
// The Python solution reduces the count to 2 * C(n-1, k) modulo 1e9+7, with
// zero ways when k exceeds the n-1 other people. Precompute factorials and
// inverse factorials using Fermat inverses. int64 is used for modular products.
// Time: O(n + log MOD). Space: O(n).
//
// @lc code=start

const mod3881 int64 = 1_000_000_007

func CountVisiblePeople3881(n int, pos int, k int) int {
	total := n - 1
	if k > total {
		return 0
	}

	factorial := make([]int64, total+1)
	factorial[0] = 1
	for value := 1; value <= total; value++ {
		factorial[value] = factorial[value-1] * int64(value) % mod3881
	}

	inverseFactorial := make([]int64, total+1)
	inverseFactorial[total] = powMod3881(factorial[total], mod3881-2)
	for value := total; value > 0; value-- {
		inverseFactorial[value-1] = inverseFactorial[value] * int64(value) % mod3881
	}

	combinations := factorial[total]
	combinations = combinations * inverseFactorial[k] % mod3881
	combinations = combinations * inverseFactorial[total-k] % mod3881
	return int(2 * combinations % mod3881)
}

func powMod3881(base int64, exp int64) int64 {
	result := int64(1)
	for exp > 0 {
		if exp&1 == 1 {
			result = result * base % mod3881
		}
		base = base * base % mod3881
		exp >>= 1
	}
	return result
}

// @lc code=end
