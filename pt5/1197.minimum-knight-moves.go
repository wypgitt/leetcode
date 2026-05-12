package main

func minKnightMoves(x int, y int) int {
	if x < 0 {
		x = -x
	}
	if y < 0 {
		y = -y
	}
	if x == 0 && y == 0 {
		return 0
	}

	type state struct {
		row      int
		col      int
		distance int
	}

	moves := [][2]int{{1, 2}, {2, 1}, {2, -1}, {1, -2}, {-1, -2}, {-2, -1}, {-2, 1}, {-1, 2}}
	queue := []state{{row: 0, col: 0, distance: 0}}
	visited := map[[2]int]bool{{0, 0}: true}

	for head := 0; head < len(queue); head++ {
		current := queue[head]
		for _, move := range moves {
			nextRow := current.row + move[0]
			nextCol := current.col + move[1]
			if nextRow == x && nextCol == y {
				return current.distance + 1
			}
			key := [2]int{nextRow, nextCol}
			if nextRow >= -2 && nextRow <= x+2 && nextCol >= -2 && nextCol <= y+2 && !visited[key] {
				visited[key] = true
				queue = append(queue, state{row: nextRow, col: nextCol, distance: current.distance + 1})
			}
		}
	}
	return -1
}

