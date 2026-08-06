package leetcode

//
// @lc app=leetcode id=368 lang=golang
//
// [368] Largest Divisible Subset
//
// Notes
// Sort the values and run longest-chain DP. If nums[i] is divisible by nums[j],
// any best subset ending at j can be extended by i; parent pointers reconstruct
// the actual subset. Sorting gives transitivity, so adjacent divisibility in the
// chain implies pairwise divisibility. Time: O(n^2). Space: O(n).
//
// @lc code=start

import "sort"

func LargestDivisibleSubset368(nums []int) []int {
	sort.Ints(nums)
	n := len(nums)
	if n == 0 {
		return nil
	}

	dp := make([]int, n)
	parent := make([]int, n)
	bestIndex := 0
	for i := range nums {
		dp[i] = 1
		parent[i] = -1
		for j := 0; j < i; j++ {
			if nums[i]%nums[j] == 0 && dp[j]+1 > dp[i] {
				dp[i] = dp[j] + 1
				parent[i] = j
			}
		}
		if dp[i] > dp[bestIndex] {
			bestIndex = i
		}
	}

	answer := []int{}
	for current := bestIndex; current != -1; current = parent[current] {
		answer = append(answer, nums[current])
	}
	for left, right := 0, len(answer)-1; left < right; left, right = left+1, right-1 {
		answer[left], answer[right] = answer[right], answer[left]
	}
	return answer
}

// @lc code=end
