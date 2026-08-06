package leetcode

// ReachNumber754 uses the fact that after k moves the farthest right position
// is S=1+...+k. Flipping selected moves reduces S by twice their sum, so target
// is reachable iff S>=target and S-target is even.
//
// Time: O(sqrt(target)). Space: O(1).
func ReachNumber754(target int) int {
	target = absInt(target)
	step, total := 0, 0
	for total < target || (total-target)%2 != 0 {
		step++
		total += step
	}
	return step
}
