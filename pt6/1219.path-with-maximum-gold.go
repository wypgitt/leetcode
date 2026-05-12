package main

func getMaximumGold(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	best := 0
	dirs := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}

	var dfs func(int, int) int
	dfs = func(r, c int) int {
		gold := grid[r][c]
		grid[r][c] = 0
		bestNext := 0

		for _, d := range dirs {
			nr, nc := r+d[0], c+d[1]
			if nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] > 0 {
				if got := dfs(nr, nc); got > bestNext {
					bestNext = got
				}
			}
		}

		grid[r][c] = gold
		return gold + bestNext
	}

	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if grid[r][c] > 0 {
				if got := dfs(r, c); got > best {
					best = got
				}
			}
		}
	}

	return best
}

/*
Explanation

Use DFS backtracking from every gold cell. During one path, set the current
cell to 0 to mark it visited, explore neighbors, then restore the original
gold before returning.

Backtracking is necessary because a locally large neighbor may block a better
overall path. The grid itself acts as the visited set, which keeps the Go code
compact and avoids allocating a map for every path.

Edge cases: all zero cells return 0; isolated gold cells are valid paths; the
best path may start anywhere, so we try every nonzero cell.

Time complexity: exponential in the number of gold cells, often described as
O(g * 3^g) because after the first move each path has at most three unvisited
directions.
Space complexity: O(g) recursion depth.
*/
