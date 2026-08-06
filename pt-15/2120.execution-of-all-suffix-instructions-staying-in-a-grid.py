#
# @lc app=leetcode id=2120 lang=python3
#
# [2120] Execution of All Suffix Instructions Staying in a Grid
#
# https://leetcode.com/problems/execution-of-all-suffix-instructions-staying-in-a-grid/description/
#
# algorithms
# Medium (82.08%)
# Likes:    572
# Dislikes: 54
# Total Accepted:    40K
# Total Submissions: 48.8K
# Testcase Example:  "3\n[0,1]\n\"RRDDLU\""
#
# There is an n x n grid, with the top-left cell at (0, 0) and the bottom-right
# cell at (n - 1, n - 1). You are given the integer n and an integer array
# startPos where startPos = [start_row, start_col] indicates that a robot is
# initially at cell (start_row, start_col).
#
# You are also given a 0-indexed string s of length m where s[i] is the i^th
# instruction for the robot: 'L' (move left), 'R' (move right), 'U' (move up),
# and 'D' (move down).
#
# The robot can begin executing from any i^th instruction in s. It executes the
# instructions one by one towards the end of s but it stops if either of these
# conditions is met:
#
#
# The next instruction will move the robot off the grid.
#
#
# There are no more instructions left to execute.
#
# Return an array answer of length m where answer[i] is the number of
# instructions the robot can execute if the robot begins executing from the i^th
# instruction in s.
#
#
#
# Example 1:
#
# Input: n = 3, startPos = [0,1], s = "RRDDLU"
# Output: [1,5,4,3,1,0]
# Explanation: Starting from startPos and beginning execution from the i^th
# instruction:
# - 0^th: "RRDDLU". Only one instruction "R" can be executed before it moves off
# the grid.
# - 1^st:  "RDDLU". All five instructions can be executed while it stays in the
# grid and ends at (1, 1).
# - 2^nd:   "DDLU". All four instructions can be executed while it stays in the
# grid and ends at (1, 0).
# - 3^rd:    "DLU". All three instructions can be executed while it stays in the
# grid and ends at (0, 0).
# - 4^th:     "LU". Only one instruction "L" can be executed before it moves off
# the grid.
# - 5^th:      "U". If moving up, it would move off the grid.
#
# Example 2:
#
# Input: n = 2, startPos = [1,1], s = "LURD"
# Output: [4,1,0,0]
# Explanation:
# - 0^th: "LURD".
# - 1^st:  "URD".
# - 2^nd:   "RD".
# - 3^rd:    "D".
#
# Example 3:
#
# Input: n = 1, startPos = [0,0], s = "LRUD"
# Output: [0,0,0,0]
# Explanation: No matter which instruction the robot begins execution from, it
# would move off the grid.
#
#
#
# Constraints:
#
#
# m == s.length
#
#
# 1 <= n, m <= 500
#
#
# startPos.length == 2
#
#
# 0 <= start_row, start_col < n
#
#
# s consists of 'L', 'R', 'U', and 'D'.
#


# @lc code=start
from typing import List


class Solution:
    def executeInstructions(self, n: int, startPos: List[int], s: str) -> List[int]:
        """
        Interview explanation:
        For each start index i in instruction string s, simulate moving from
        startPos following s[i:], count steps until move would leave the n×n grid.

        Algorithm:
        - For each i, simulate; O(m^2) acceptable for m<=500.

        Complexity: O(m^2) time, O(1) extra space.
        """
        m = len(s)
        move = {'L': (0, -1), 'R': (0, 1), 'U': (-1, 0), 'D': (1, 0)}
        ans = [0] * m
        for i in range(m):
            r, c = startPos
            steps = 0
            for j in range(i, m):
                dr, dc = move[s[j]]
                nr, nc = r + dr, c + dc
                if not (0 <= nr < n and 0 <= nc < n):
                    break
                r, c = nr, nc
                steps += 1
            ans[i] = steps
        return ans
# @lc code=end

