#
# @lc app=leetcode id=1861 lang=python3
#
# [1861] Rotating the Box
#
# https://leetcode.com/problems/rotating-the-box/description/
#
# algorithms
# Medium (82.46%)
# Likes:    1857
# Dislikes: 88
# Total Accepted:    270K
# Total Submissions: 328K
# Testcase Example:  "[[\"#\",\".\",\"#\"]]"
#
# You are given an m x n matrix of characters boxGrid representing a side-view
# of a box. Each cell of the box is one of the following:
#
# A stone '#'
#
# A stationary obstacle '*'
#
# Empty '.'
#
# The box is rotated 90 degrees clockwise, causing some of the stones to fall
# due to gravity. Each stone falls down until it lands on an obstacle, another
# stone, or the bottom of the box. Gravity does not affect the obstacles'
# positions, and the inertia from the box's rotation does not affect the
# stones' horizontal positions.
#
# It is guaranteed that each stone in boxGrid rests on an obstacle, another
# stone, or the bottom of the box.
#
# Return an n x m matrix representing the box after the rotation described
# above.
#
# Example 1:
#
# Input: boxGrid = [["#",".","#"]]
# Output: [["."],
# ["#"],
# ["#"]]
#
# Example 2:
#
# Input: boxGrid = [["#",".","*","."],
# ["#","#","*","."]]
# Output: [["#","."],
# ["#","#"],
# ["*","*"],
# [".","."]]
#
# Example 3:
#
# Input: boxGrid = [["#","#","*",".","*","."],
# ["#","#","#","*",".","."],
# ["#","#","#",".","#","."]]
# Output: [[".","#","#"],
# [".","#","#"],
# ["#","#","*"],
# ["#","*","."],
# ["#",".","*"],
# ["#",".","."]]
#
# Constraints:
#
# m == boxGrid.length
#
# n == boxGrid[i].length
#
# 1 <= m, n <= 500
#
# boxGrid[i][j] is either '#', '*', or '.'.
#

# @lc code=start
from typing import List


class Solution:
    def rotateTheBox(self, boxGrid: List[List[str]]) -> List[List[str]]:
        """
        Interview explanation:
        Stones '#' fall right due to gravity (blocked by '*' or wall), then
        rotate the box 90° clockwise.

        Algorithm:
        - Per row: two-pointer write from right, place stones against obstacles.
        - Rotate: result[j][m-1-i] = box[i][j].

        Complexity: O(m*n) time/space.
        """
        m, n = len(boxGrid), len(boxGrid[0])
        for r in range(m):
            write = n - 1
            for c in range(n - 1, -1, -1):
                if boxGrid[r][c] == "*":
                    write = c - 1
                elif boxGrid[r][c] == "#":
                    boxGrid[r][c] = "."
                    boxGrid[r][write] = "#"
                    write -= 1
        return [[boxGrid[m - 1 - i][j] for i in range(m)] for j in range(n)]

    def rotateTheBox_simulate(self, boxGrid: List[List[str]]) -> List[List[str]]:
        """
        Interview explanation:
        Alternate: rotate first, then let stones fall down column-wise.

        Algorithm:
        - Rotate 90° CW; for each col, compact '#' downward against '*'/floor.

        Complexity: O(m*n) time/space.
        """
        m, n = len(boxGrid), len(boxGrid[0])
        rot = [[boxGrid[m - 1 - i][j] for i in range(m)] for j in range(n)]
        R, C = n, m
        for c in range(C):
            write = R - 1
            for r in range(R - 1, -1, -1):
                if rot[r][c] == "*":
                    write = r - 1
                elif rot[r][c] == "#":
                    rot[r][c] = "."
                    rot[write][c] = "#"
                    write -= 1
        return rot
# @lc code=end
