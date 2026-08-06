package leetcode

//
// @lc app=leetcode id=3785 lang=golang
//
// [3785] Minimum Swaps to Avoid Forbidden Values
//
// Notes
// A value x is feasible only if count(nums,x)+count(forbidden,x) <= n. Among
// currently bad positions where nums[i] == forbidden[i], one swap can fix at
// most two bad positions and at most one bad position of any single value. The
// optimum is therefore max(ceil(bad/2), maxBadSameValue) after feasibility.
// Go maps implement Python Counter behavior. Time: O(n). Space: O(n).
//
// @lc code=start

func MinSwaps3785(nums []int, forbidden []int) int {
	n := len(nums)
	numsCount := map[int]int{}
	forbiddenCount := map[int]int{}
	for i, value := range nums {
		numsCount[value]++
		forbiddenCount[forbidden[i]]++
	}

	for value, count := range numsCount {
		if count+forbiddenCount[value] > n {
			return -1
		}
	}
	for value, count := range forbiddenCount {
		if count+numsCount[value] > n {
			return -1
		}
	}

	badCount := map[int]int{}
	badTotal := 0
	maxBadCount := 0
	for i, value := range nums {
		if value == forbidden[i] {
			badCount[value]++
			badTotal++
			if badCount[value] > maxBadCount {
				maxBadCount = badCount[value]
			}
		}
	}

	half := (badTotal + 1) / 2
	if maxBadCount > half {
		return maxBadCount
	}
	return half
}

// @lc code=end
