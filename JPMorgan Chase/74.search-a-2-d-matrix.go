package leetcode

// SearchMatrix74 treats the matrix as one sorted flattened array. Binary-search
// index mid maps back to row mid/n and column mid%n.
//
// Time: O(log(m*n)). Space: O(1).
func SearchMatrix74(matrix [][]int, target int) bool {
	m, n := len(matrix), len(matrix[0])
	l, r := 0, m*n-1
	for l <= r {
		mid := (l + r) / 2
		v := matrix[mid/n][mid%n]
		if v == target {
			return true
		}
		if v < target {
			l = mid + 1
		} else {
			r = mid - 1
		}
	}
	return false
}
