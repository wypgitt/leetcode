#
# @lc app=leetcode id=3394 lang=python3
#
# [3394] Check if Grid can be Cut into Sections
#
# https://leetcode.com/problems/check-if-grid-can-be-cut-into-sections/description/
#
# algorithms
# Medium (68.26%)
# Likes:    631
# Dislikes: 38
# Total Accepted:    114.2K
# Total Submissions: 167.3K
# Testcase Example:  "5\n[[1,0,5,2],[0,2,2,4],[3,2,5,3],[0,4,4,5]]"
#
#
# You are given an integer n representing the dimensions of an n x n grid,
# with the origin at the bottom-left corner of the grid. You are also
# given a 2D array of coordinates rectangles, where rectangles[i] is in
# the form [start_x, start_y, end_x, end_y], representing a rectangle on
# the grid. Each rectangle is defined as follows:
#
# (start_x, start_y): The bottom-left corner of the rectangle.
#
# (end_x, end_y): The top-right corner of the rectangle.
#
# Note that the rectangles do not overlap. Your task is to determine if it
# is possible to make either two horizontal or two vertical cuts on the
# grid such that:
#
# Each of the three resulting sections formed by the cuts contains at
# least one rectangle.
#
# Every rectangle belongs to exactly one section.
#
# Return true if such cuts can be made; otherwise, return false.
#
# Example 1:
#
# Input: n = 5, rectangles = [[1,0,5,2],[0,2,2,4],[3,2,5,3],[0,4,4,5]]
#
# Output: true
#
# Explanation:
#
# The grid is shown in the diagram. We can make horizontal cuts at y = 2
# and y = 4. Hence, output is true.
#
# Example 2:
#
# Input: n = 4, rectangles = [[0,0,1,1],[2,0,3,4],[0,2,2,3],[3,0,4,3]]
#
# Output: true
#
# Explanation:
#
# We can make vertical cuts at x = 2 and x = 3. Hence, output is true.
#
# Example 3:
#
# Input: n = 4, rectangles =
# [[0,2,2,4],[1,0,3,2],[2,2,3,4],[3,0,4,2],[3,2,4,4]]
#
# Output: false
#
# Explanation:
#
# We cannot make two horizontal or two vertical cuts that satisfy the
# conditions. Hence, output is false.
#
# Constraints:
#
# 3 <= n <= 10^9
#
# 3 <= rectangles.length <= 10^5
#
# 0 <= rectangles[i][0] < rectangles[i][2] <= n
#
# 0 <= rectangles[i][1] < rectangles[i][3] <= n
#
# No two rectangles overlap.
#

# @lc code=start

from typing import List


class Solution:
    def checkValidCuts(self, n: int, rectangles: List[List[int]]) -> bool:
        """
        Interview explanation:
        Rectangles do not overlap. Two vertical (or horizontal) cuts make three
        non-empty sections iff the projection intervals on that axis can be
        ordered with at least two gaps between merged groups.

        Algorithm:
        - Project to [start_x, end_x] and [start_y, end_y].
        - Sort by start, sweep merge; count times a new interval starts at/after
          current max end — need >= 2 such gaps.

        Complexity: O(m log m) time, O(m) space.
        """
        xs = [(r[0], r[2]) for r in rectangles]
        ys = [(r[1], r[3]) for r in rectangles]
        return self._can_cut(xs) or self._can_cut(ys)

    def _can_cut(self, intervals: List[tuple]) -> bool:
        intervals.sort()
        gaps = 0
        max_end = intervals[0][1]
        for start, end in intervals[1:]:
            if start >= max_end:
                gaps += 1
                if gaps >= 2:
                    return True
            max_end = max(max_end, end)
        return False
# @lc code=end
