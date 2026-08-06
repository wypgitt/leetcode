package leetcode

//
// @lc app=leetcode id=356 lang=golang
//
// [356] Line Reflection
//
// Notes
// The mirror line, if it exists, is forced by the minimum and maximum x values:
// its doubled x-coordinate is minX + maxX. Store each point in a Go map keyed
// by a small struct, then verify that every point's reflected partner is also
// present. The map is Go's hash-set replacement for Python's set.
// Time: O(n). Space: O(n).
//
// @lc code=start

type point356 struct {
	x int
	y int
}

func IsReflected356(points [][]int) bool {
	if len(points) <= 1 {
		return true
	}

	minX, maxX := points[0][0], points[0][0]
	seen := make(map[point356]struct{}, len(points))

	for _, p := range points {
		x, y := p[0], p[1]
		if x < minX {
			minX = x
		}
		if x > maxX {
			maxX = x
		}
		seen[point356{x: x, y: y}] = struct{}{}
	}

	axisSum := minX + maxX
	for p := range seen {
		if _, ok := seen[point356{x: axisSum - p.x, y: p.y}]; !ok {
			return false
		}
	}
	return true
}

// @lc code=end
