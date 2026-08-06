package leetcode

// GrayCode89 uses the binary-reflected formula i ^ (i >> 1), which changes
// exactly one bit between adjacent generated integers.
//
// Time: O(2^n). Space: O(1) excluding output.
func GrayCode89(n int) []int {
	ans := make([]int, 1<<n)
	for i := range ans {
		ans[i] = i ^ (i >> 1)
	}
	return ans
}
