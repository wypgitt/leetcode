package leetcode

// CombinationSum3_216 backtracks over increasing digits 1..9, using each at most
// once. Pruning stops when a number exceeds remaining sum or too few digits are
// left to complete k values.
//
// Time: O(C(9,k)*k). Space: O(k).
func CombinationSum3_216(k int, n int) [][]int {
	ans := [][]int{}
	path := []int{}
	var dfs func(int, int)
	dfs = func(start, rem int) {
		if len(path) == k {
			if rem == 0 {
				ans = append(ans, append([]int(nil), path...))
			}
			return
		}
		need := k - len(path)
		for num := start; num < 10; num++ {
			if num > rem || 10-num < need {
				break
			}
			path = append(path, num)
			dfs(num+1, rem-num)
			path = path[:len(path)-1]
		}
	}
	dfs(1, n)
	return ans
}
