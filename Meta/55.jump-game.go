package leetcode

// CanJump55 tracks the farthest reachable index while scanning. If the scan ever
// reaches an index beyond farthest, that index and the end are unreachable.
//
// Time: O(n). Space: O(1).
func CanJump55(nums []int) bool {
	far := 0
	for i, j := range nums {
		if i > far {
			return false
		}
		far = maxInt(far, i+j)
		if far >= len(nums)-1 {
			return true
		}
	}
	return true
}
