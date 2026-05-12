/*
 * 1039. Minimum Score Triangulation of Polygon
 */
class Solution {
    public int minScoreTriangulation(int[] values) {
        int n = values.length;
        int[][] dp = new int[n][n];

        for (int gap = 2; gap < n; gap++) {
            for (int left = 0; left + gap < n; left++) {
                int right = left + gap;
                dp[left][right] = Integer.MAX_VALUE;

                for (int mid = left + 1; mid < right; mid++) {
                    int score =
                        dp[left][mid] +
                        dp[mid][right] +
                        values[left] * values[mid] * values[right];
                    dp[left][right] = Math.min(dp[left][right], score);
                }
            }
        }

        return dp[0][n - 1];
    }
}

/*
Interview Explanation

Core idea:
For a polygon interval from left to right, choose the triangle that uses edge
(left, right). Its third vertex mid splits the polygon into two independent
sub-polygons.

Java data structures:
- int[][] dp is an interval DP table. dp[left][right] stores the minimum score
  to triangulate the chain of vertices from left through right.

Algorithm:
1. Process intervals by increasing gap.
2. For each interval [left, right] with at least three vertices, try every
   mid between them.
3. Combine the left interval, right interval, and triangle product.
4. Store the minimum.

Correctness:
Every triangulation of [left, right] has exactly one triangle touching edge
(left, right), with some mid as the third vertex. Removing that triangle leaves
two smaller independent triangulation problems. Trying all mid choices and
using optimal subproblem scores therefore considers every triangulation and
chooses the minimum.

Complexity:
There are O(n^2) intervals and O(n) mid choices per interval, so time is
O(n^3). Space is O(n^2).

Edge cases:
- n = 3: exactly one triangle.
- n = 4: chooses between the two diagonals.
- Maximum n = 50 is well within O(n^3).
*/
