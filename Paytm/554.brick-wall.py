#
# @lc app=leetcode id=554 lang=python3
#
# [554] Brick Wall
#
# https://leetcode.com/problems/brick-wall/description/
#
# algorithms
# Medium (56.07%)
# Likes:    2687
# Dislikes: 186
# Total Accepted:    175K
# Total Submissions: 313K
# Testcase Example:  "[[1,2,2,1],[3,1,2],[1,3,2],[2,4],[3,1,2],[1,3,1,1]]"
#
# There is a rectangular brick wall in front of you with n rows of bricks. The
# i^th row has some number of bricks each of the same height (i.e., one unit)
# but they can be of different widths. The total width of each row is the same.
#
# Draw a vertical line from the top to the bottom and cross the least bricks.
# If your line goes through the edge of a brick, then the brick is not
# considered as crossed. You cannot draw a line just along one of the two
# vertical edges of the wall, in which case the line will obviously cross no
# bricks.
#
# Given the 2D array wall that contains the information about the wall, return
# the minimum number of crossed bricks after drawing such a vertical line.
#
# Example 1:
#
# Input: wall = [[1,2,2,1],[3,1,2],[1,3,2],[2,4],[3,1,2],[1,3,1,1]]
# Output: 2
#
# Example 2:
#
# Input: wall = [[1],[1],[1]]
# Output: 3
#
# Constraints:
#
# n == wall.length
#
# 1 <= n <= 10^4
#
# 1 <= wall[i].length <= 10^4
#
# 1 <= sum(wall[i].length) <= 2 * 10^4
#
# sum(wall[i]) is the same for each row i.
#
# 1 <= wall[i][j] <= 2^31 - 1
#

# @lc code=start
from collections import defaultdict
from typing import List
class Solution:
    def leastBricks(self, wall: List[List[int]]) -> int:
        """
        Interview explanation:
        A vertical line through the wall crosses fewest bricks when it passes
        through the most aligned edges (not at the wall ends). Count edge
        positions across rows; answer = rows - max edge frequency.

        Algorithm:
        - For each row, accumulate prefix widths excluding the last brick;
          count frequency of each edge position.
        - Return len(wall) - max(count.values() or 0).

        Complexity: O(total bricks) time, O(distinct edges) space.
        """
        edges = defaultdict(int)
        for row in wall:
            pos = 0
            for brick in row[:-1]:
                pos += brick
                edges[pos] += 1
        return len(wall) - (max(edges.values()) if edges else 0)
# @lc code=end

