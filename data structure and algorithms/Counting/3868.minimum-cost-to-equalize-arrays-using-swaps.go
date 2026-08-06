package leetcode

//
// @lc app=leetcode id=3868 lang=golang
//
// [3868] Minimum Cost to Equalize Arrays Using Swaps
//
// Notes
// For each value, the combined frequency across both arrays must be even;
// otherwise equal target multisets are impossible. If nums1 has more than half
// the combined count of a value, those excess copies must be swapped out, and
// each such excess contributes one operation in the Python algorithm. Go maps
// replace Counter. Time: O(n). Space: O(n).
//
// @lc code=start

func MinCost3868(nums1 []int, nums2 []int) int {
	count1 := map[int]int{}
	count2 := map[int]int{}
	for _, value := range nums1 {
		count1[value]++
	}
	for _, value := range nums2 {
		count2[value]++
	}

	cost := 0
	seen := map[int]struct{}{}
	for value := range count1 {
		seen[value] = struct{}{}
	}
	for value := range count2 {
		seen[value] = struct{}{}
	}

	for value := range seen {
		total := count1[value] + count2[value]
		if total%2 == 1 {
			return -1
		}
		target := total / 2
		if count1[value] > target {
			cost += count1[value] - target
		}
	}
	return cost
}

// @lc code=end
