package main

func countServers(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	rowCount := make([]int, rows)
	colCount := make([]int, cols)

	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if grid[r][c] == 1 {
				rowCount[r]++
				colCount[c]++
			}
		}
	}

	total := 0
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if grid[r][c] == 1 && (rowCount[r] > 1 || colCount[c] > 1) {
				total++
			}
		}
	}

	return total
}

/*
Explanation

A server communicates if another server exists in the same row or column.
Precompute row server counts and column server counts. Then each server can be
classified in O(1).

The two count slices are the right data structure because they avoid scanning a
row and column for every server.

Edge cases: isolated server is not counted; two servers in the same row both
count; all-zero grid returns 0.

Time complexity: O(mn).
Space complexity: O(m+n).
*/
