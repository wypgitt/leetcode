package leetcode

// TwoSum167 uses two pointers on the sorted array. A low sum moves left forward;
// a high sum moves right backward. Returned indices are 1-based.
//
// Time: O(n). Space: O(1).
func TwoSum167(numbers []int, target int) []int {
	l, r := 0, len(numbers)-1
	for l < r {
		sum := numbers[l] + numbers[r]
		if sum == target {
			return []int{l + 1, r + 1}
		}
		if sum < target {
			l++
		} else {
			r--
		}
	}
	return []int{}
}
