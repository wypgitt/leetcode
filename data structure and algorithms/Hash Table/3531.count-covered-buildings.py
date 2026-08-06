#
# @lc app=leetcode id=3531 lang=python3
#
# [3531] Count Covered Buildings
#
# https://leetcode.com/problems/count-covered-buildings/description/
#
# algorithms
# Medium (58.80%)
# Likes:    452
# Dislikes: 28
# Total Accepted:    106K
# Total Submissions: 180.2K
# Testcase Example:  "3\n[[1,2],[2,2],[3,2],[2,1],[2,3]]"
#
#
# You are given a positive integer n, representing an n x n city. You are
# also given a 2D grid buildings, where buildings[i] = [x, y] denotes a
# unique building located at coordinates [x, y].
#
# A building is covered if there is at least one building in all four
# directions: left, right, above, and below.
#
# Return the number of covered buildings.
#
# Example 1:
#
# Input: n = 3, buildings = [[1,2],[2,2],[3,2],[2,1],[2,3]]
#
# Output: 1
#
# Explanation:
#
# Only building [2,2] is covered as it has at least one building:
#
# above ([1,2])
#
# below ([3,2])
#
# left ([2,1])
#
# right ([2,3])
#
# Thus, the count of covered buildings is 1.
#
# Example 2:
#
# Input: n = 3, buildings = [[1,1],[1,2],[2,1],[2,2]]
#
# Output: 0
#
# Explanation:
#
# No building has at least one building in all four directions.
#
# Example 3:
#
# Input: n = 5, buildings = [[1,3],[3,2],[3,3],[3,5],[5,3]]
#
# Output: 1
#
# Explanation:
#
# Only building [3,3] is covered as it has at least one building:
#
# above ([1,3])
#
# below ([5,3])
#
# left ([3,2])
#
# right ([3,5])
#
# Thus, the count of covered buildings is 1.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= buildings.length <= 10^5
#
# buildings[i] = [x, y]
#
# 1 <= x, y <= n
#
# All coordinates of buildings are unique.
#

# @lc code=start
from typing import List


class Solution:
    def countCoveredBuildings(self, n: int, buildings: List[List[int]]) -> int:
        """
        Interview explanation:
        A building is covered iff some other building shares its row on both
        left and right and its column above and below. Track min/max y per row
        and min/max x per column.

        Algorithm:
        - Aggregate min/max y for each x, min/max x for each y.
        - Count buildings strictly inside those ranges on both axes.

        Complexity: O(b) time, O(b) space for b buildings.
        """
        row_min = {}
        row_max = {}
        col_min = {}
        col_max = {}
        for x, y in buildings:
            if x not in row_min:
                row_min[x] = row_max[x] = y
            else:
                row_min[x] = min(row_min[x], y)
                row_max[x] = max(row_max[x], y)
            if y not in col_min:
                col_min[y] = col_max[y] = x
            else:
                col_min[y] = min(col_min[y], x)
                col_max[y] = max(col_max[y], x)

        ans = 0
        for x, y in buildings:
            if row_min[x] < y < row_max[x] and col_min[y] < x < col_max[y]:
                ans += 1
        return ans
# @lc code=end
