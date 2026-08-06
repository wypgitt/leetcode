#
# @lc app=leetcode id=296 lang=python3
#
# [296] Best Meeting Point
#
# https://leetcode.com/problems/best-meeting-point/description/
#
# algorithms
# Hard (61.45%)
# Likes:    1218
# Dislikes: 108
# Total Accepted:    98.3K
# Total Submissions: 160K
# Testcase Example:  "[[1,0,0,0,1],[0,0,0,0,0],[0,0,1,0,0]]"
#
#
# Given an m x n binary grid grid where each 1 marks the home of one
# friend, return the minimal total travel distance.
#
# The total travel distance is the sum of the distances between the houses
# of the friends and the meeting point.
#
# The distance is calculated using Manhattan Distance, where distance(p1,
# p2) = |p2.x - p1.x| + |p2.y - p1.y|.
#
# Example 1:
#
# Input: grid = [[1,0,0,0,1],[0,0,0,0,0],[0,0,1,0,0]]
# Output: 6
# Explanation: Given three friends living at (0,0), (0,4), and (2,2).
# The point (0,2) is an ideal meeting point, as the total travel distance
# of 2 + 2 + 2 = 6 is minimal.
# So return 6.
#
# Example 2:
#
# Input: grid = [[1,1]]
# Output: 1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 200
#
# grid[i][j] is either 0 or 1.
#
# There will be at least two friends in the grid.
#
# @lc code=start
from typing import List


class Solution:
    def minTotalDistance(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Manhattan distance separates into independent row and column problems.
        Optimal meeting point is at the median of all home rows and median of
        all home columns.

        Algorithm:
        - Collect sorted row indices (scan row-major) and sorted col indices
          (scan column-major) of all 1s.
        - Sum |x - median| over rows and over cols.

        Complexity: O(mn) time, O(p) space for p people.
        """
        rows, cols = [], []
        m, n = len(grid), len(grid[0])
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 1:
                    rows.append(i)
        for j in range(n):
            for i in range(m):
                if grid[i][j] == 1:
                    cols.append(j)

        def dist_to_median(arr: List[int]) -> int:
            med = arr[len(arr) // 2]
            return sum(abs(x - med) for x in arr)

        return dist_to_median(rows) + dist_to_median(cols)
# @lc code=end

