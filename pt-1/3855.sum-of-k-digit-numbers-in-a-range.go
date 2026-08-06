package leetcode

//
// @lc app=leetcode id=3855 lang=golang
//
// [3855] Sum of K-Digit Numbers in a Range
//
// Notes
// The sum of chosen digits from [l,r] is the arithmetic-series sum. For every
// position, the other k-1 positions can be chosen independently in count^(k-1)
// ways; multiplying by the repunit 111..1 places the same digit contribution in
// every decimal position. Modular inverse of 9 builds the repunit. Time:
// O(log k). Space: O(1).
//
// @lc code=start

const mod3855 int64 = 1_000_000_007

func SumOfNumbers3855(l int, r int, k int) int {
	count := int64(r - l + 1)
	digitSum := int64(l+r) * count / 2
	otherPositions := powMod3855(count%mod3855, int64(k-1))
	repunit := (powMod3855(10, int64(k)) - 1 + mod3855) % mod3855
	repunit = repunit * powMod3855(9, mod3855-2) % mod3855
	return int(digitSum % mod3855 * otherPositions % mod3855 * repunit % mod3855)
}

func powMod3855(base int64, exp int64) int64 {
	result := int64(1)
	base %= mod3855
	for exp > 0 {
		if exp&1 == 1 {
			result = result * base % mod3855
		}
		base = base * base % mod3855
		exp >>= 1
	}
	return result
}

// @lc code=end
