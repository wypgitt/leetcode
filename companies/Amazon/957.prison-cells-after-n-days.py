#
# @lc app=leetcode id=957 lang=python3
#
# [957] Prison Cells After N Days
#
# https://leetcode.com/problems/prison-cells-after-n-days/description/
#
# algorithms
# Medium (39.26%)
# Likes:    1570
# Dislikes: 1782
# Total Accepted:    179K
# Total Submissions: 455K
# Testcase Example:  "[0,1,0,1,1,0,0,1]"
#
# There are 8 prison cells in a row and each cell is either occupied or vacant.
#
# Each day, whether the cell is occupied or vacant changes according to the
# following rules:
#
# If a cell has two adjacent neighbors that are both occupied or both vacant,
# then the cell becomes occupied.
#
# Otherwise, it becomes vacant.
#
# Note that because the prison is a row, the first and the last cells in the
# row can't have two adjacent neighbors.
#
# You are given an integer array cells where cells[i] == 1 if the i^th cell is
# occupied and cells[i] == 0 if the i^th cell is vacant, and you are given an
# integer n.
#
# Return the state of the prison after n days (i.e., n such changes described
# above).
#
# Example 1:
#
# Input: cells = [0,1,0,1,1,0,0,1], n = 7
# Output: [0,0,1,1,0,0,0,0]
# Explanation: The following table summarizes the state of the prison on each
# day:
# Day 0: [0, 1, 0, 1, 1, 0, 0, 1]
# Day 1: [0, 1, 1, 0, 0, 0, 0, 0]
# Day 2: [0, 0, 0, 0, 1, 1, 1, 0]
# Day 3: [0, 1, 1, 0, 0, 1, 0, 0]
# Day 4: [0, 0, 0, 0, 0, 1, 0, 0]
# Day 5: [0, 1, 1, 1, 0, 1, 0, 0]
# Day 6: [0, 0, 1, 0, 1, 1, 0, 0]
# Day 7: [0, 0, 1, 1, 0, 0, 0, 0]
#
# Example 2:
#
# Input: cells = [1,0,0,1,0,0,1,0], n = 1000000000
# Output: [0,0,1,1,1,1,1,0]
#
# Constraints:
#
# cells.length == 8
#
# cells[i] is either 0 or 1.
#
# 1 <= n <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def prisonAfterNDays(self, cells: List[int], n: int) -> List[int]:
        """
        Interview explanation:
        Each day, interior cell becomes 1 iff neighbors equal; ends become 0.
        Only 2^6 reachable states ⇒ a cycle appears; detect it and jump ahead
        with modulo on the remaining days.

        Algorithm (cycle detection):
        - seen[state] = day index when first observed
        - For day in 0..n-1: if state seen: remaining = (n-day) % cycle; simulate
          remaining steps; return
        - Else record, advance one day

        Complexity: O(2^6) time/space.
        """
        def nxt(c: List[int]) -> List[int]:
            return [0] + [1 if c[i - 1] == c[i + 1] else 0 for i in range(1, 7)] + [0]

        seen = {}
        day = 0
        while day < n:
            key = tuple(cells)
            if key in seen:
                cycle = day - seen[key]
                remaining = (n - day) % cycle
                for _ in range(remaining):
                    cells = nxt(cells)
                return cells
            seen[key] = day
            cells = nxt(cells)
            day += 1
        return cells
# @lc code=end



