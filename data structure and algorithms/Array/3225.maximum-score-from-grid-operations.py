#
# @lc app=leetcode id=3225 lang=python3
#
# [3225] Maximum Score From Grid Operations
#
# https://leetcode.com/problems/maximum-score-from-grid-operations/description/
#
# algorithms
# Hard (64.22%)
# Likes:    201
# Dislikes: 24
# Total Accepted:    50.2K
# Total Submissions: 78.2K
# Testcase Example:  "[[0,0,0,0,0],[0,0,3,0,0],[0,1,0,0,0],[5,0,0,3,0],[0,0,0,0,2]]"
#
#
# You are given a 2D matrix grid of size n x n. Initially, all cells of
# the grid are colored white. In one operation, you can select any cell of
# indices (i, j), and color black all the cells of the j^th column
# starting from the top row down to the i^th row.
#
# The grid score is the sum of all grid[i][j] such that cell (i, j) is
# white and it has a horizontally adjacent black cell.
#
# Return the maximum score that can be achieved after some number of
# operations.
#
# Example 1:
#
# Input: grid =
# [[0,0,0,0,0],[0,0,3,0,0],[0,1,0,0,0],[5,0,0,3,0],[0,0,0,0,2]]
#
# Output: 11
#
# Explanation:
#
# In the first operation, we color all cells in column 1 down to row 3,
# and in the second operation, we color all cells in column 4 down to the
# last row. The score of the resulting grid is grid[3][0] + grid[1][2] +
# grid[3][3] which is equal to 11.
#
# Example 2:
#
# Input: grid =
# [[10,9,0,0,15],[7,1,0,8,0],[5,20,0,11,0],[0,0,0,1,2],[8,12,1,10,3]]
#
# Output: 94
#
# Explanation:
#
# We perform operations on 1, 2, and 3 down to rows 1, 4, and 0,
# respectively. The score of the resulting grid is grid[0][0] + grid[1][0]
# + grid[2][1] + grid[4][1] + grid[1][3] + grid[2][3] + grid[3][3] +
# grid[4][3] + grid[0][4] which is equal to 94.
#
# Constraints:
#
# 1 <= n == grid.length <= 100
#
# n == grid[i].length
#
# 0 <= grid[i][j] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumScore(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Each column chooses a black prefix height. White cells score only when a
        horizontal neighbor is black. Process columns L->R with DP on heights,
        tracking whether the previous column's white cells were already scored.

        Algorithm:
        - prefix[j][i] = sum of first i cells in column j.
        - prevPick[h] / prevSkip[h]: best score ending with previous height h,
          with / without having scored that column's whites via the next column.
        - Transition on (curr, prev) heights: if curr > prev, score whites in
          column j-1 on [prev, curr); else score whites in column j on [curr, prev).

        Complexity: O(n^3) time, O(n^2) space.
        Alternate: DP over consecutive column height pairs with prefix/suffix maxima.
        """
        n = len(grid)
        prefix = [[0] * (n + 1) for _ in range(n)]
        for j in range(n):
            for i in range(n):
                prefix[j][i + 1] = prefix[j][i] + grid[i][j]

        prev_pick = [0] * (n + 1)
        prev_skip = [0] * (n + 1)

        for j in range(1, n):
            curr_pick = [0] * (n + 1)
            curr_skip = [0] * (n + 1)
            for curr in range(n + 1):
                for prev in range(n + 1):
                    if curr > prev:
                        score = prefix[j - 1][curr] - prefix[j - 1][prev]
                        curr_pick[curr] = max(curr_pick[curr], prev_skip[prev] + score)
                        curr_skip[curr] = max(curr_skip[curr], prev_skip[prev] + score)
                    else:
                        score = prefix[j][prev] - prefix[j][curr]
                        curr_pick[curr] = max(curr_pick[curr], prev_pick[prev] + score)
                        curr_skip[curr] = max(curr_skip[curr], prev_pick[prev])
            prev_pick, prev_skip = curr_pick, curr_skip

        return max(prev_pick)

# @lc code=end
