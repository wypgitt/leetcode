package leetcode

// FindDerangement634 uses D(n) = (n-1)*(D(n-1)+D(n-2)) with rolling state.
// D(0)=1 and D(1)=0 are the recurrence bases.
//
// Time: O(n). Space: O(1).
func FindDerangement634(n int) int {
	const mod = 1000000007
	if n == 1 {
		return 0
	}
	prev2, prev1 := 1, 0
	for i := 2; i <= n; i++ {
		cur := (i - 1) * (prev1 + prev2) % mod
		prev2, prev1 = prev1, cur
	}
	return prev1
}
