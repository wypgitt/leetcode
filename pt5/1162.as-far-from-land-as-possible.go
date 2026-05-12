package main

func maxDistance(grid [][]int) int {
	n := len(grid)
	type point struct {
		row int
		col int
	}
	queue := []point{}

	for r := 0; r < n; r++ {
		for c := 0; c < n; c++ {
			if grid[r][c] == 1 {
				queue = append(queue, point{row: r, col: c})
			}
		}
	}

	if len(queue) == 0 || len(queue) == n*n {
		return -1
	}

	directions := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	distance := -1
	for len(queue) > 0 {
		distance++
		levelSize := len(queue)
		for i := 0; i < levelSize; i++ {
			current := queue[0]
			queue = queue[1:]
			for _, direction := range directions {
				nextRow := current.row + direction[0]
				nextCol := current.col + direction[1]
				if nextRow >= 0 && nextRow < n && nextCol >= 0 && nextCol < n && grid[nextRow][nextCol] == 0 {
					grid[nextRow][nextCol] = 1
					queue = append(queue, point{row: nextRow, col: nextCol})
				}
			}
		}
	}

	return distance
}

