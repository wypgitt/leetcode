package leetcode

//
// @lc app=leetcode id=3865 lang=golang
//
// [3865] Reverse K Subarrays
//
// Notes
// The Python code splits nums into k equal-length blocks where block length is
// len(nums)/k, reverses each block, and appends it to the result. The Go
// translation mirrors that exactly with slice indexing. Time: O(n). Space:
// O(n).
//
// @lc code=start

func ReverseSubarrays3865(nums []int, k int) []int {
	blockLength := len(nums) / k
	result := make([]int, 0, len(nums))

	for start := 0; start < len(nums); start += blockLength {
		end := start + blockLength
		if end > len(nums) {
			end = len(nums)
		}
		for i := end - 1; i >= start; i-- {
			result = append(result, nums[i])
		}
	}

	return result
}

// @lc code=end
