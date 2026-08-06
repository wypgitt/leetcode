package leetcode

// MaxArea11 uses two pointers. The area is limited by the shorter wall, so with
// fixed width endpoints, moving the taller wall cannot improve the limiting
// height; only the shorter wall is worth moving inward.
//
// Time: O(n). Space: O(1).
func MaxArea11(height []int) int {
	l, r, best := 0, len(height)-1, 0
	for l < r {
		h := minInt(height[l], height[r])
		best = maxInt(best, (r-l)*h)
		if height[l] < height[r] {
			l++
		} else {
			r--
		}
	}
	return best
}
