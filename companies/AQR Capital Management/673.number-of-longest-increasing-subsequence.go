package leetcode

// FindNumberOfLIS673 tracks the best LIS length ending at each index and how
// many such subsequences exist. A better predecessor length replaces the count;
// an equal predecessor length adds to it.
//
// Time: O(n^2). Space: O(n).
func FindNumberOfLIS673(nums []int) int {
	n := len(nums)
	if n == 0 {
		return 0
	}
	lengths := make([]int, n)
	counts := make([]int, n)
	for i := range nums {
		lengths[i], counts[i] = 1, 1
		for j := 0; j < i; j++ {
			if nums[j] < nums[i] {
				if lengths[j]+1 > lengths[i] {
					lengths[i] = lengths[j] + 1
					counts[i] = counts[j]
				} else if lengths[j]+1 == lengths[i] {
					counts[i] += counts[j]
				}
			}
		}
	}
	longest := 0
	for _, l := range lengths {
		longest = maxInt(longest, l)
	}
	ans := 0
	for i, l := range lengths {
		if l == longest {
			ans += counts[i]
		}
	}
	return ans
}
