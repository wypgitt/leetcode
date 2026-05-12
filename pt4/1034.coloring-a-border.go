package main

/*
1034. Coloring A Border
*/
func colorBorder(grid [][]int, row int, col int, color int) [][]int {
	rows, cols := len(grid), len(grid[0])
	original := grid[row][col]
	visited := make([][]bool, rows)
	for r := range visited {
		visited[r] = make([]bool, cols)
	}

	directions := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	stack := [][2]int{{row, col}}
	borders := make([][2]int, 0)
	visited[row][col] = true

	for len(stack) > 0 {
		cell := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		r, c := cell[0], cell[1]
		isBorder := r == 0 || r == rows-1 || c == 0 || c == cols-1

		for _, direction := range directions {
			nextRow := r + direction[0]
			nextCol := c + direction[1]

			if nextRow < 0 || nextRow >= rows || nextCol < 0 || nextCol >= cols {
				isBorder = true
			} else if grid[nextRow][nextCol] != original {
				isBorder = true
			} else if !visited[nextRow][nextCol] {
				visited[nextRow][nextCol] = true
				stack = append(stack, [2]int{nextRow, nextCol})
			}
		}

		if isBorder {
			borders = append(borders, cell)
		}
	}

	for _, cell := range borders {
		grid[cell[0]][cell[1]] = color
	}

	return grid
}

/*
Interview Explanation

Core idea:
Find the connected component containing (row, col). A cell in that component
is a border if it is on the grid edge or touches a cell outside the component.

Go data structures:
- [][]bool visited keeps traversal state separate from grid colors.
- [][2]int stack implements iterative DFS.
- [][2]int borders stores cells to recolor after traversal, avoiding accidental
  interference with component detection.

Algorithm:
1. DFS through cells with the original color.
2. For each component cell, inspect four neighbors.
3. Mark it as a border if a neighbor is out of bounds or has a different color.
4. Recolor only collected border cells.

Correctness:
DFS visits exactly the starting connected component because it only moves
through same-color adjacent cells. The border test matches the definition
directly. Therefore recoloring the collected cells changes every and only
border cell of that component.

Complexity:
Each cell is visited at most once, so time is O(m*n). visited, stack, and
borders use O(m*n) space in the worst case.

Edge cases:
- Single-cell grid: the only cell is a border.
- Whole grid same color: only outer ring changes.
- If color equals original, the returned grid is unchanged but still correct.
*/
