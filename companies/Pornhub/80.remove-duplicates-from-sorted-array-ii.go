package leetcode

// RemoveDuplicates80 writes each value if fewer than two values have been kept
// or if it differs from the value two positions before write. Sorted order makes
// this enough to keep at most two of each value.
//
// Time: O(n). Space: O(1).
func RemoveDuplicates80(nums []int) int {
	write := 0
	for _, x := range nums {
		if write < 2 || x != nums[write-2] {
			nums[write] = x
			write++
		}
	}
	return write
}
