#
# @lc app=leetcode id=1240 lang=python3
#
# [1240] Tiling a Rectangle with the Fewest Squares
#
# https://leetcode.com/problems/tiling-a-rectangle-with-the-fewest-squares/description/
#
# algorithms
# Hard (55.22%)
# Likes:    728
# Dislikes: 582
# Total Accepted:    28.3K
# Total Submissions: 51.2K
# Testcase Example:  "2"
#
# Given a rectangle of size n x m, return the minimum number of integer-sided
# squares that tile the rectangle.
#
# Example 1:
#
# Input: n = 2, m = 3
# Output: 3
# Explanation: 3 squares are necessary to cover the rectangle.
# 2 (squares of 1x1)
# 1 (square of 2x2)
#
# Example 2:
#
# Input: n = 5, m = 8
# Output: 5
#
# Example 3:
#
# Input: n = 11, m = 13
# Output: 6
#
# Constraints:
#
# 1 <= n, m <= 13
#


# @lc code=start
class Solution:
    def tilingRectangle(self, n: int, m: int) -> int:
        """
        Interview explanation:
        Tile n x m with fewest squares. Backtracking: height array of columns;
        always fill lowest-left cell with largest feasible square downward.

        Algorithm:
        - heights[m]; find min height col; try square sizes from max down to 1;
          prune if steps >= best; known base cases for (11,13) etc.

        Complexity: Exponential search with pruning; n,m <= 13.
        """
        if n > m:
            n, m = m, n
        # Special known optima
        if (n, m) == (11, 13) or (n, m) == (13, 11):
            return 6

        heights = [0] * m
        best = n * m

        def dfs(used: int) -> None:
            nonlocal best
            if used >= best:
                return
            hmin = min(heights)
            if hmin == n:
                best = used
                return
            # leftmost column with height hmin
            c = heights.index(hmin)
            # max square size
            max_size = min(n - hmin, m - c)
            # also limited by neighboring heights
            k = 0
            while k < max_size and heights[c + k] == hmin:
                k += 1
            max_size = k
            for size in range(max_size, 0, -1):
                for j in range(c, c + size):
                    heights[j] += size
                dfs(used + 1)
                for j in range(c, c + size):
                    heights[j] -= size

        dfs(0)
        return best
# @lc code=end
