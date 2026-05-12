package main

func countSquares(matrix [][]int) int {
	rows, cols := len(matrix), len(matrix[0])
	prev := make([]int, cols+1)
	total := 0

	for r := 1; r <= rows; r++ {
		curr := make([]int, cols+1)
		for c := 1; c <= cols; c++ {
			if matrix[r-1][c-1] == 1 {
				curr[c] = 1 + min3(prev[c], curr[c-1], prev[c-1])
				total += curr[c]
			}
		}
		prev = curr
	}

	return total
}

func min3(a, b, c int) int {
	if b < a {
		a = b
	}
	if c < a {
		a = c
	}
	return a
}

/*
Explanation

dp[r][c] is the largest all-ones square ending at cell r,c. If the cell is 1,
the square can extend only as far as the minimum of the top, left, and
top-left neighboring DP values plus one.

Every cell with DP value x contributes x squares ending there: side lengths 1
through x. The implementation keeps only the previous row and current row,
because those are the only DP states needed.

Edge cases: zero cells contribute 0; one-row or one-column matrices work; all
ones count many nested squares.

Time complexity: O(mn).
Space complexity: O(n).
*/
