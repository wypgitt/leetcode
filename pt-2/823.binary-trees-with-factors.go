package leetcode

import "sort"

// NumFactoredBinaryTrees823 sorts values so factor subtree counts are already
// known. For root x, each factor pair a*b=x combines dp[a]*dp[b] trees; unequal
// factors are doubled for left/right order.
//
// Time: O(n^2) worst case. Space: O(n).
func NumFactoredBinaryTrees823(arr []int) int {
	const mod = 1000000007
	sort.Ints(arr)
	dp := map[int]int{}
	values := map[int]bool{}
	for _, x := range arr {
		values[x] = true
	}
	for _, x := range arr {
		total := 1
		for _, a := range arr {
			if a*a > x {
				break
			}
			if x%a == 0 {
				b := x / a
				if values[b] {
					ways := dp[a] * dp[b] % mod
					if a == b {
						total = (total + ways) % mod
					} else {
						total = (total + 2*ways) % mod
					}
				}
			}
		}
		dp[x] = total
	}
	ans := 0
	for _, v := range dp {
		ans = (ans + v) % mod
	}
	return ans
}
