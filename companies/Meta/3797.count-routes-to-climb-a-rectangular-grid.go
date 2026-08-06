package leetcode

//
// @lc app=leetcode id=3797 lang=golang
//
// [3797] Count Routes to Climb a Rectangular Grid
//
// Notes
// Dynamic programming moves upward row by row. For each row, prefix sums provide
// all horizontal choices within distance d; moving to the row above uses radius
// floor(sqrt(d^2-1)) because one vertical step is already spent. Blocked cells
// receive zero ways. Time: O(RC). Space: O(C).
//
// @lc code=start

func NumberOfRoutes3797(grid []string, d int) int {
	const mod = 1_000_000_007
	rowCount, colCount := len(grid), len(grid[0])
	horizontalRadius := d
	upwardRadius := isqrt3797(d*d - 1)

	rangeSums := func(values []int, radius int, row string) []int {
		prefix := make([]int, colCount+1)
		for col, value := range values {
			prefix[col+1] = (prefix[col] + value) % mod
		}

		result := make([]int, colCount)
		for col := 0; col < colCount; col++ {
			if row[col] == '#' {
				continue
			}
			left := col - radius
			if left < 0 {
				left = 0
			}
			right := col + radius
			if right >= colCount {
				right = colCount - 1
			}
			result[col] = (prefix[right+1] - prefix[left] + mod) % mod
		}
		return result
	}

	enter := make([]int, colCount)
	for col := 0; col < colCount; col++ {
		if grid[rowCount-1][col] == '.' {
			enter[col] = 1
		}
	}

	for row := rowCount - 1; row >= 0; row-- {
		afterHorizontal := rangeSums(enter, horizontalRadius, grid[row])
		if row == 0 {
			total := 0
			for _, value := range afterHorizontal {
				total = (total + value) % mod
			}
			return total
		}
		enter = rangeSums(afterHorizontal, upwardRadius, grid[row-1])
	}

	return 0
}

func isqrt3797(x int) int {
	if x <= 0 {
		return 0
	}
	lo, hi := 1, x
	for lo <= hi {
		mid := lo + (hi-lo)/2
		if mid <= x/mid {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return hi
}

// @lc code=end
