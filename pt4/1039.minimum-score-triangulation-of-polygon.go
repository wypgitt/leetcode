package main

/*
1039. Minimum Score Triangulation of Polygon
*/
func minScoreTriangulation(values []int) int {
	n := len(values)
	dp := make([][]int, n)
	for i := range dp {
		dp[i] = make([]int, n)
	}

	for gap := 2; gap < n; gap++ {
		for left := 0; left+gap < n; left++ {
			right := left + gap
			best := int(^uint(0) >> 1)

			for mid := left + 1; mid < right; mid++ {
				score := dp[left][mid] + dp[mid][right] + values[left]*values[mid]*values[right]
				if score < best {
					best = score
				}
			}

			dp[left][right] = best
		}
	}

	return dp[0][n-1]
}

/*
Interview Explanation

Core idea:
For an interval of polygon vertices [left, right], choose the triangle that
uses edge (left, right). Its third vertex mid splits the polygon into two
independent smaller polygons.

Go data structures:
- [][]int dp is an interval DP table. dp[left][right] stores the minimum score
  to triangulate that vertex interval.

Algorithm:
1. Process intervals by increasing length.
2. For each interval with at least three vertices, try every possible mid.
3. Combine left subproblem, right subproblem, and triangle product.
4. Store the minimum score.

Correctness:
Every triangulation of [left, right] contains exactly one triangle using edge
(left, right), with some third vertex mid. Removing that triangle leaves two
independent sub-polygons. The recurrence tries every possible mid and uses
optimal subproblem scores, so it considers every triangulation and chooses the
minimum.

Complexity:
There are O(n^2) intervals and O(n) split choices, so time is O(n^3). Space is
O(n^2).

Edge cases:
- n = 3 returns the single triangle product.
- n = 4 chooses between two diagonals.
- n <= 50 is comfortable for O(n^3).
*/
