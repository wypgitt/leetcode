package leetcode

// Permute46 chooses one unused number for each position. A bool slice gives O(1)
// used checks; the path is copied only at complete permutations.
//
// Time: O(n!*n). Space: O(n) excluding output.
func Permute46(nums []int) [][]int {
	ans := [][]int{}
	path := []int{}
	used := make([]bool, len(nums))
	var dfs func()
	dfs = func() {
		if len(path) == len(nums) {
			ans = append(ans, append([]int(nil), path...))
			return
		}
		for i, v := range nums {
			if used[i] {
				continue
			}
			used[i] = true
			path = append(path, v)
			dfs()
			path = path[:len(path)-1]
			used[i] = false
		}
	}
	dfs()
	return ans
}
