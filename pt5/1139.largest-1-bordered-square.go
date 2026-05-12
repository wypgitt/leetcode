package main

func largest1BorderedSquare(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	horizontal := make([][]int, rows)
	vertical := make([][]int, rows)
	for r := 0; r < rows; r++ {
		horizontal[r] = make([]int, cols)
		vertical[r] = make([]int, cols)
	}

	bestSide := 0
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if grid[r][c] == 0 {
				continue
			}
			horizontal[r][c] = 1
			vertical[r][c] = 1
			if c > 0 {
				horizontal[r][c] += horizontal[r][c-1]
			}
			if r > 0 {
				vertical[r][c] += vertical[r-1][c]
			}

			side := horizontal[r][c]
			if vertical[r][c] < side {
				side = vertical[r][c]
			}
			for side > bestSide {
				if vertical[r][c-side+1] >= side && horizontal[r-side+1][c] >= side {
					bestSide = side
					break
				}
				side--
			}
		}
	}

	return bestSide * bestSide
}

