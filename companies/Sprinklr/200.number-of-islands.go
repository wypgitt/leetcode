package leetcode

// NumIslands200 scans for land, increments island count, and sinks that whole
// connected component with an explicit DFS stack. Mutating visited land to '0'
// keeps auxiliary visited space unnecessary.
//
// Time: O(m*n). Space: O(m*n) worst-case stack.
func NumIslands200(grid [][]byte) int {
	if len(grid) == 0 || len(grid[0]) == 0 {
		return 0
	}
	rows, cols := len(grid), len(grid[0])
	islands := 0
	dirs := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	type cell struct{ r, c int }
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if grid[r][c] != '1' {
				continue
			}
			islands++
			grid[r][c] = '0'
			st := []cell{{r, c}}
			for len(st) > 0 {
				cur := st[len(st)-1]
				st = st[:len(st)-1]
				for _, d := range dirs {
					nr, nc := cur.r+d[0], cur.c+d[1]
					if nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == '1' {
						grid[nr][nc] = '0'
						st = append(st, cell{nr, nc})
					}
				}
			}
		}
	}
	return islands
}
