#
# @lc app=leetcode id=3212 lang=python3
#
# [3212] Count Submatrices With Equal Frequency of X and Y
#
# https://leetcode.com/problems/count-submatrices-with-equal-frequency-of-x-and-y/description/
#
# algorithms
# Medium (69.74%)
# Likes:    423
# Dislikes: 51
# Total Accepted:    108.7K
# Total Submissions: 155.9K
# Testcase Example:  "[[\"X\",\"Y\",\".\"],[\"Y\",\".\",\".\"]]"
#
#
# Given a 2D character matrix grid, where grid[i][j] is either 'X', 'Y',
# or '.', return the number of submatrices that contain:
#
# grid[0][0]
#
# an equal frequency of 'X' and 'Y'.
#
# at least one 'X'.
#
# Example 1:
#
# Input: grid = [["X","Y","."],["Y",".","."]]
#
# Output: 3
#
# Explanation:
#
# Example 2:
#
# Input: grid = [["X","X"],["X","Y"]]
#
# Output: 0
#
# Explanation:
#
# No submatrix has an equal frequency of 'X' and 'Y'.
#
# Example 3:
#
# Input: grid = [[".","."],[".","."]]
#
# Output: 0
#
# Explanation:
#
# No submatrix has at least one 'X'.
#
# Constraints:
#
# 1 <= grid.length, grid[i].length <= 1000
#
# grid[i][j] is either 'X', 'Y', or '.'.
#

# @lc code=start
from typing import List


class Solution:
    def numberOfSubmatrices(self, grid: List[List[str]]) -> int:
        """
        Interview explanation:
        Count submatrices that include grid[0][0], have equal # of 'X' and 'Y',
        and at least one 'X'. Including (0,0) means only top-left prefixes
        grid[0..i][0..j].

        Algorithm:
        - 2D prefix counts of X and Y.
        - For each (i,j), if prefix_X == prefix_Y and prefix_X > 0, count it.

        Complexity: O(m * n) time and space.
        """
        m, n = len(grid), len(grid[0])
        px = [[0] * (n + 1) for _ in range(m + 1)]
        py = [[0] * (n + 1) for _ in range(m + 1)]
        ans = 0
        for i in range(m):
            for j in range(n):
                px[i + 1][j + 1] = (
                    px[i][j + 1] + px[i + 1][j] - px[i][j] + (1 if grid[i][j] == "X" else 0)
                )
                py[i + 1][j + 1] = (
                    py[i][j + 1] + py[i + 1][j] - py[i][j] + (1 if grid[i][j] == "Y" else 0)
                )
                if px[i + 1][j + 1] == py[i + 1][j + 1] and px[i + 1][j + 1] > 0:
                    ans += 1
        return ans
# @lc code=end
