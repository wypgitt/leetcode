package leetcode

// MinCost256 keeps the minimum total ending with each color. The next red cost
// can only come from previous blue/green, and similarly for other colors.
//
// Time: O(n). Space: O(1).
func MinCost256(costs [][]int) int {
	if len(costs) == 0 {
		return 0
	}
	red, blue, green := 0, 0, 0
	for _, c := range costs {
		r, b, g := c[0], c[1], c[2]
		red, blue, green = r+minInt(blue, green), b+minInt(red, green), g+minInt(red, blue)
	}
	return minInt(red, minInt(blue, green))
}
