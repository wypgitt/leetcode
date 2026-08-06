package leetcode

//
// @lc app=leetcode id=391 lang=golang
//
// [391] Perfect Rectangle
//
// Notes
// A perfect cover has total small-rectangle area equal to the bounding box area,
// and every internal corner appears an even number of times. Toggle all four
// corners of every rectangle in a hash set; only the four bounding corners
// should remain. Time: O(n). Space: O(n).
//
// @lc code=start

type point391 struct {
	x int
	y int
}

func IsRectangleCover391(rectangles [][]int) bool {
	minX, minY := 1<<60, 1<<60
	maxX, maxY := -1<<60, -1<<60
	totalArea := 0
	corners := map[point391]struct{}{}

	toggle := func(point point391) {
		if _, ok := corners[point]; ok {
			delete(corners, point)
		} else {
			corners[point] = struct{}{}
		}
	}

	for _, rect := range rectangles {
		x1, y1, x2, y2 := rect[0], rect[1], rect[2], rect[3]
		if x1 < minX {
			minX = x1
		}
		if y1 < minY {
			minY = y1
		}
		if x2 > maxX {
			maxX = x2
		}
		if y2 > maxY {
			maxY = y2
		}

		totalArea += (x2 - x1) * (y2 - y1)
		toggle(point391{x: x1, y: y1})
		toggle(point391{x: x1, y: y2})
		toggle(point391{x: x2, y: y1})
		toggle(point391{x: x2, y: y2})
	}

	boundingArea := (maxX - minX) * (maxY - minY)
	if totalArea != boundingArea || len(corners) != 4 {
		return false
	}

	for _, point := range []point391{
		{x: minX, y: minY},
		{x: minX, y: maxY},
		{x: maxX, y: minY},
		{x: maxX, y: maxY},
	} {
		if _, ok := corners[point]; !ok {
			return false
		}
	}
	return true
}

// @lc code=end
