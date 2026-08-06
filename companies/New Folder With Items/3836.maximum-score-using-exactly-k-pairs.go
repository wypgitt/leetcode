package leetcode

//
// @lc app=leetcode id=3836 lang=golang
//
// [3836] Maximum Score Using Exactly K Pairs
//
// Notes
// This is a two-sequence pairing DP. For each required pair count, cur[i][j]
// stores the best score using prefixes nums1[:i], nums2[:j]. Each state either
// skips from the top/left or pairs nums1[i-1] with nums2[j-1] on top of the
// previous pair-count layer. Time: O(k*n*m). Space: O(n*m).
//
// @lc code=start

func MaxScore3836(nums1 []int, nums2 []int, k int) int {
	n, m := len(nums1), len(nums2)
	const negInf = -1 << 60

	prev := make([][]int, n+1)
	for i := range prev {
		prev[i] = make([]int, m+1)
	}

	for pairs := 1; pairs <= k; pairs++ {
		cur := make([][]int, n+1)
		for i := range cur {
			cur[i] = make([]int, m+1)
			for j := range cur[i] {
				cur[i][j] = negInf
			}
		}

		for i := pairs; i <= n; i++ {
			x := nums1[i-1]
			for j := pairs; j <= m; j++ {
				take := prev[i-1][j-1] + x*nums2[j-1]
				cur[i][j] = max3836(cur[i-1][j], cur[i][j-1], take)
			}
		}
		prev = cur
	}

	return prev[n][m]
}

func max3836(values ...int) int {
	best := values[0]
	for _, value := range values[1:] {
		if value > best {
			best = value
		}
	}
	return best
}

// @lc code=end
