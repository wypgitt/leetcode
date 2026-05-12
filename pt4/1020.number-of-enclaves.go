package main

/*
1020. Number of Enclaves
*/
func numEnclaves(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	directions := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}

	eraseBoundaryComponent := func(startRow, startCol int) {
		if grid[startRow][startCol] == 0 {
			return
		}

		stack := [][2]int{{startRow, startCol}}
		grid[startRow][startCol] = 0

		for len(stack) > 0 {
			cell := stack[len(stack)-1]
			stack = stack[:len(stack)-1]

			for _, direction := range directions {
				nextRow := cell[0] + direction[0]
				nextCol := cell[1] + direction[1]

				if nextRow >= 0 && nextRow < rows &&
					nextCol >= 0 && nextCol < cols &&
					grid[nextRow][nextCol] == 1 {
					grid[nextRow][nextCol] = 0
					stack = append(stack, [2]int{nextRow, nextCol})
				}
			}
		}
	}

	for row := 0; row < rows; row++ {
		eraseBoundaryComponent(row, 0)
		eraseBoundaryComponent(row, cols-1)
	}
	for col := 0; col < cols; col++ {
		eraseBoundaryComponent(0, col)
		eraseBoundaryComponent(rows-1, col)
	}

	answer := 0
	for _, row := range grid {
		for _, cell := range row {
			answer += cell
		}
	}
	return answer
}

/*
Interview Explanation

Core idea:
An enclave is land that cannot reach the boundary. Instead of checking every
land cell, reverse the question: every land cell connected to the boundary can
escape. Remove those cells, then count the land that remains.

Go data structures:
- [][]int stores the grid and doubles as a visited marker by flipping visited
  land from 1 to 0.
- [][2]int is used as an explicit DFS stack. This is safer than recursion for
  a 500 x 500 grid because Go's growing stack is good, but an iterative stack
  keeps control obvious in an interview.

Algorithm:
1. Start DFS from every boundary land cell.
2. During DFS, mark reachable land as water.
3. Sum all remaining cells. Only enclosed land remains.

Correctness:
Every erased land cell has a path of land cells to the boundary, so it is not
an enclave. Any land cell that remains cannot have such a path, because the
boundary DFS for its component would have reached and erased it. Therefore the
final sum is exactly the number of enclave cells.

Complexity:
Each grid cell is visited at most once, so time is O(m*n). The stack can hold
O(m*n) cells in the worst case. The algorithm modifies the grid in place.

Edge cases:
- All water returns 0.
- All land is fully erased from the boundary.
- Single row or column has no enclaves.
- Interior islands surrounded by water remain counted.
*/
