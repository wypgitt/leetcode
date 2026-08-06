package leetcode

//
// @lc app=leetcode id=3905 lang=golang
//
// [3905] Multi-Source Flood Fill
//
// Notes
// Run BFS from all colored sources at once. During each time layer, collect
// proposed colors for unvisited neighbors and keep the maximum color proposed
// for each cell; after the layer, apply those proposals and enqueue the cells.
// This preserves simultaneous expansion semantics. Time: O(nm). Space: O(nm).
//
// @lc code=start

func ColorGrid3905(n int, m int, sources [][]int) [][]int {
	grid := make([][]int, n)
	dist := make([][]int, n)
	for row := 0; row < n; row++ {
		grid[row] = make([]int, m)
		dist[row] = make([]int, m)
		for col := 0; col < m; col++ {
			dist[row][col] = -1
		}
	}

	queue := [][2]int{}
	for _, source := range sources {
		row, col, color := source[0], source[1], source[2]
		grid[row][col] = color
		dist[row][col] = 0
		queue = append(queue, [2]int{row, col})
	}

	directions := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	time := 0
	for len(queue) > 0 {
		proposals := map[int]int{}
		levelSize := len(queue)
		for i := 0; i < levelSize; i++ {
			cell := queue[0]
			queue = queue[1:]
			row, col := cell[0], cell[1]
			color := grid[row][col]
			for _, d := range directions {
				nr, nc := row+d[0], col+d[1]
				if 0 <= nr && nr < n && 0 <= nc && nc < m && dist[nr][nc] == -1 {
					key := nr*m + nc
					if color > proposals[key] {
						proposals[key] = color
					}
				}
			}
		}

		time++
		for key, color := range proposals {
			row, col := key/m, key%m
			if dist[row][col] == -1 {
				dist[row][col] = time
				grid[row][col] = color
				queue = append(queue, [2]int{row, col})
			}
		}
	}

	return grid
}

// @lc code=end
