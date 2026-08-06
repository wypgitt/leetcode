package leetcode

// ArrayNesting565 follows permutation links and marks visited indices by
// writing -1, which is outside the valid value range 0..n-1. Each index belongs
// to exactly one cycle/component.
//
// The input slice is mutated to keep O(1) auxiliary space.
// Time: O(n). Space: O(1).
func ArrayNesting565(nums []int) int {
	best := 0
	for i := range nums {
		if nums[i] == -1 {
			continue
		}
		count, j := 0, i
		for nums[j] != -1 {
			next := nums[j]
			nums[j] = -1
			j = next
			count++
		}
		best = maxInt(best, count)
	}
	return best
}
