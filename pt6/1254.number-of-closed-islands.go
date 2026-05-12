package main

func closedIsland(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	dirs := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}

	var flood func(int, int)
	flood = func(r, c int) {
		stack := [][2]int{{r, c}}
		grid[r][c] = 1
		for len(stack) > 0 {
			cell := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			for _, d := range dirs {
				nr, nc := cell[0]+d[0], cell[1]+d[1]
				if nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 0 {
					grid[nr][nc] = 1
					stack = append(stack, [2]int{nr, nc})
				}
			}
		}
	}

	for r := 0; r < rows; r++ {
		if grid[r][0] == 0 {
			flood(r, 0)
		}
		if grid[r][cols-1] == 0 {
			flood(r, cols-1)
		}
	}
	for c := 0; c < cols; c++ {
		if grid[0][c] == 0 {
			flood(0, c)
		}
		if grid[rows-1][c] == 0 {
			flood(rows-1, c)
		}
	}

	count := 0
	for r := 1; r < rows-1; r++ {
		for c := 1; c < cols-1; c++ {
			if grid[r][c] == 0 {
				count++
				flood(r, c)
			}
		}
	}

	return count
}

/*
Explanation

Land is 0 and water is 1. Any land connected to the border cannot be closed, so
first flood-fill border-connected land into water. Then every remaining land
component inside the grid is one closed island; count it and flood it.

An explicit stack avoids recursion-depth issues. The grid itself is the
visited structure because changing 0 to 1 marks land as processed.

Edge cases: land touching any border is not closed; diagonal contact does not
connect components; all-water grids return 0.

Time complexity: O(mn).
Space complexity: O(mn) worst-case stack.
*/
