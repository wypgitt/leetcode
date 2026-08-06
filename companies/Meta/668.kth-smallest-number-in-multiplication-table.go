package leetcode

//
// @lc app=leetcode id=668 lang=golang
//
// [668] Kth Smallest Number in Multiplication Table
//
// Notes
// Binary search the answer value. For a candidate x, row i contributes
// min(n, x/i) values <= x. This count is monotone, so the smallest x with count
// at least k is the k-th table value. Iterate the smaller dimension as rows for
// speed. Time: O(min(m,n) log(mn)). Space: O(1).
//
// @lc code=start

func FindKthNumber668(m int, n int, k int) int {
	if m > n {
		m, n = n, m
	}

	countLessOrEqual := func(value int) int {
		count := 0
		for row := 1; row <= m; row++ {
			rowCount := value / row
			if rowCount > n {
				rowCount = n
			}
			count += rowCount
		}
		return count
	}

	left, right := 1, m*n
	for left < right {
		middle := left + (right-left)/2
		if countLessOrEqual(middle) >= k {
			right = middle
		} else {
			left = middle + 1
		}
	}
	return left
}

// @lc code=end
