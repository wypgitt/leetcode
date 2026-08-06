package leetcode

// NextPermutation31 finds the first pivot from the right where nums[i] <
// nums[i+1], swaps it with the smallest larger suffix value, then reverses the
// suffix to make the next lexicographic permutation minimal.
//
// Time: O(n). Space: O(1).
func NextPermutation31(nums []int) {
	i := len(nums) - 2
	for i >= 0 && nums[i] >= nums[i+1] {
		i--
	}
	if i >= 0 {
		j := len(nums) - 1
		for nums[j] <= nums[i] {
			j--
		}
		nums[i], nums[j] = nums[j], nums[i]
	}
	for l, r := i+1, len(nums)-1; l < r; l, r = l+1, r-1 {
		nums[l], nums[r] = nums[r], nums[l]
	}
}
