package leetcode

import "sort"

// ValidSquare593 checks the six pairwise squared distances. A square has four
// equal positive side lengths and two equal diagonals, each twice the side's
// squared length. Squared distances avoid floating point.
//
// Time: O(1). Space: O(1).
func ValidSquare593(p1 []int, p2 []int, p3 []int, p4 []int) bool {
	points := [][]int{p1, p2, p3, p4}
	dists := make([]int, 0, 6)
	for i := 0; i < 4; i++ {
		for j := i + 1; j < 4; j++ {
			dx := points[i][0] - points[j][0]
			dy := points[i][1] - points[j][1]
			dists = append(dists, dx*dx+dy*dy)
		}
	}
	sort.Ints(dists)
	return dists[0] > 0 && dists[0] == dists[1] && dists[1] == dists[2] && dists[2] == dists[3] && dists[4] == dists[5] && dists[4] == 2*dists[0]
}
