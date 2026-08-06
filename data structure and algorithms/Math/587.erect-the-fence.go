package leetcode

//
// @lc app=leetcode id=587 lang=golang
//
// [587] Erect the Fence
//
// Notes
// Use the monotonic chain convex hull. Sorting points lexicographically, build
// lower and upper hulls while popping only clockwise turns; collinear boundary
// points remain on the hull. A set removes duplicate endpoints before returning
// coordinates. Time: O(n log n). Space: O(n).
//
// @lc code=start

import "sort"

type point587 struct {
	x int
	y int
}

func OuterTrees587(trees [][]int) [][]int {
	points := make([]point587, len(trees))
	for i, point := range trees {
		points[i] = point587{x: point[0], y: point[1]}
	}
	sort.Slice(points, func(i, j int) bool {
		if points[i].x != points[j].x {
			return points[i].x < points[j].x
		}
		return points[i].y < points[j].y
	})

	if len(points) <= 3 {
		answer := make([][]int, len(points))
		for i, point := range points {
			answer[i] = []int{point.x, point.y}
		}
		return answer
	}

	lower := []point587{}
	for _, point := range points {
		for len(lower) >= 2 && cross587(lower[len(lower)-2], lower[len(lower)-1], point) < 0 {
			lower = lower[:len(lower)-1]
		}
		lower = append(lower, point)
	}

	upper := []point587{}
	for i := len(points) - 1; i >= 0; i-- {
		point := points[i]
		for len(upper) >= 2 && cross587(upper[len(upper)-2], upper[len(upper)-1], point) < 0 {
			upper = upper[:len(upper)-1]
		}
		upper = append(upper, point)
	}

	boundary := map[point587]struct{}{}
	for _, point := range lower {
		boundary[point] = struct{}{}
	}
	for _, point := range upper {
		boundary[point] = struct{}{}
	}

	answer := make([][]int, 0, len(boundary))
	for point := range boundary {
		answer = append(answer, []int{point.x, point.y})
	}
	return answer
}

func cross587(a, b, c point587) int {
	return (b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x)
}

// @lc code=end
