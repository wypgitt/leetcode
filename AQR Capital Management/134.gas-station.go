package leetcode

// CanCompleteCircuit134 first checks total gas feasibility. If the running tank
// from a candidate start becomes negative at i, no station in that failed range
// can be a valid start, so the next candidate is i+1.
//
// Time: O(n). Space: O(1).
func CanCompleteCircuit134(gas []int, cost []int) int {
	total, tank, start := 0, 0, 0
	for i := range gas {
		diff := gas[i] - cost[i]
		total += diff
		tank += diff
		if tank < 0 {
			start = i + 1
			tank = 0
		}
	}
	if total < 0 {
		return -1
	}
	return start
}
