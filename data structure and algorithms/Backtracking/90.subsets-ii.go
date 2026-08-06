package leetcode

import "sort"

// SubsetsWithDup90 sorts nums so duplicates are adjacent. At each recursion
// depth, a duplicate equal to the previous value is skipped if the previous copy
// was not chosen at that same depth.
//
// Time: O(U*n), U unique subsets. Space: O(n) excluding output.
func SubsetsWithDup90(nums []int) [][]int {
	sort.Ints(nums)
	ans := [][]int{}
	path := []int{}
	var dfs func(int)
	dfs = func(start int) {
		ans = append(ans, append([]int(nil), path...))
		for i := start; i < len(nums); i++ {
			if i > start && nums[i] == nums[i-1] {
				continue
			}
			path = append(path, nums[i])
			dfs(i + 1)
			path = path[:len(path)-1]
		}
	}
	dfs(0)
	return ans
}
