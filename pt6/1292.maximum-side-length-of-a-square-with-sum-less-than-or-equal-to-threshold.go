package main

func maxSideLength(mat [][]int, threshold int) int {
	rows, cols := len(mat), len(mat[0])
	prefix := make([][]int, rows+1)
	for r := range prefix {
		prefix[r] = make([]int, cols+1)
	}

	for r := 0; r < rows; r++ {
		rowSum := 0
		for c := 0; c < cols; c++ {
			rowSum += mat[r][c]
			prefix[r+1][c+1] = prefix[r][c+1] + rowSum
		}
	}

	exists := func(size int) bool {
		for r := 0; r+size <= rows; r++ {
			for c := 0; c+size <= cols; c++ {
				sum := prefix[r+size][c+size] - prefix[r][c+size] - prefix[r+size][c] + prefix[r][c]
				if sum <= threshold {
					return true
				}
			}
		}
		return false
	}

	left, right := 0, rows
	if cols < right {
		right = cols
	}
	for left < right {
		mid := left + (right-left+1)/2
		if exists(mid) {
			left = mid
		} else {
			right = mid - 1
		}
	}
	return left
}

/*
Explanation

Build a 2D prefix-sum matrix so any square sum can be queried in O(1). Then
binary search the side length. If a square of size k exists under the
threshold, every smaller size is also possible; if none exists, larger sizes
are impossible.

The prefix matrix is the core data structure because it avoids resumming cells
for each candidate square.

Edge cases: answer 0 when no single cell fits; rectangular matrices; threshold
large enough for the largest possible square.

Time complexity: O(mn log min(m,n)).
Space complexity: O(mn).
*/
