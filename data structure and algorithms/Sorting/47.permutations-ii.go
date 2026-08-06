package leetcode

import "sort"

// PermuteUnique47 sorts nums so duplicates are adjacent. Skip nums[i] when it
// equals nums[i-1] and the previous copy has not been used in the current prefix;
// otherwise the same permutation prefix would be generated twice.
//
// Time: O(U*n), U unique permutations. Space: O(n) excluding output.
func PermuteUnique47(nums []int) [][]int {
	sort.Ints(nums)
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
			if used[i] || (i > 0 && nums[i] == nums[i-1] && !used[i-1]) {
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
