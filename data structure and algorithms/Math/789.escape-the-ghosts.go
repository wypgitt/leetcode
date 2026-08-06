package leetcode

// EscapeGhosts789 compares Manhattan distances to the target. If any ghost can
// reach the target no later than the player, it can wait there and catch the
// player; otherwise going straight to the target is safe.
//
// Time: O(g). Space: O(1).
func EscapeGhosts789(ghosts [][]int, target []int) bool {
	myDist := absInt(target[0]) + absInt(target[1])
	for _, g := range ghosts {
		if absInt(g[0]-target[0])+absInt(g[1]-target[1]) <= myDist {
			return false
		}
	}
	return true
}
