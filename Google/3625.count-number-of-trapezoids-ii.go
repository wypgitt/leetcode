package leetcode

//
// @lc app=leetcode id=3625 lang=golang
//
// [3625] Count Number of Trapezoids II
//
// Notes
// Every pair of points is a possible side/diagonal. Count unordered pairs of
// segments that lie on two different parallel lines, then subtract the pairs
// that are actually parallelogram diagonals: diagonals share a doubled midpoint
// and must not be collinear. Go maps keyed by normalized direction and midpoint
// structs replace Python tuple dictionaries. Time: O(n^2). Space: O(n^2).
//
// @lc code=start

type direction3625 struct {
	dx int
	dy int
}

type midpoint3625 struct {
	x int
	y int
}

func CountTrapezoids3625(points [][]int) int {
	linesBySlope := map[direction3625]map[int]int{}
	midpointGroups := map[midpoint3625]struct {
		total int
		byDir map[direction3625]int
	}{}

	n := len(points)
	for i := 0; i < n; i++ {
		x1, y1 := points[i][0], points[i][1]
		for j := i + 1; j < n; j++ {
			x2, y2 := points[j][0], points[j][1]
			dir := normalizeDirection3625(x2-x1, y2-y1)

			lineConstant := dir.dy*x1 - dir.dx*y1
			if linesBySlope[dir] == nil {
				linesBySlope[dir] = map[int]int{}
			}
			linesBySlope[dir][lineConstant]++

			mid := midpoint3625{x: x1 + x2, y: y1 + y2}
			group := midpointGroups[mid]
			if group.byDir == nil {
				group.byDir = map[direction3625]int{}
			}
			group.total++
			group.byDir[dir]++
			midpointGroups[mid] = group
		}
	}

	parallelSidePairs := 0
	for _, lineCounts := range linesBySlope {
		previousSegments := 0
		for _, segmentCount := range lineCounts {
			parallelSidePairs += previousSegments * segmentCount
			previousSegments += segmentCount
		}
	}

	parallelograms := 0
	for _, group := range midpointGroups {
		current := group.total * (group.total - 1) / 2
		for _, sameSlope := range group.byDir {
			current -= sameSlope * (sameSlope - 1) / 2
		}
		parallelograms += current
	}

	return parallelSidePairs - parallelograms
}

func normalizeDirection3625(dx, dy int) direction3625 {
	g := gcd3625(abs3625(dx), abs3625(dy))
	dx /= g
	dy /= g
	if dx < 0 || (dx == 0 && dy < 0) {
		dx = -dx
		dy = -dy
	}
	return direction3625{dx: dx, dy: dy}
}

func gcd3625(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	if a < 0 {
		return -a
	}
	return a
}

func abs3625(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// @lc code=end
