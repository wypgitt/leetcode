#
# @lc app=leetcode id=2337 lang=python3
#
# [2337] Move Pieces to Obtain a String
#
# https://leetcode.com/problems/move-pieces-to-obtain-a-string/description/
#
# algorithms
# Medium (56.61%)
# Likes:    1477
# Dislikes: 86
# Total Accepted:    153.1K
# Total Submissions: 270.4K
# Testcase Example:  "\"_L__R__R_\"\n\"L______RR\""
#
# You are given two strings start and target, both of length n. Each string
# consists only of the characters 'L', 'R', and '_' where:
#
#
# The characters 'L' and 'R' represent pieces, where a piece 'L' can move to the
# left only if there is a blank space directly to its left, and a piece 'R' can
# move to the right only if there is a blank space directly to its right.
#
#
# The character '_' represents a blank space that can be occupied by any of the
# 'L' or 'R' pieces.
#
# Return true if it is possible to obtain the string target by moving the pieces
# of the string start any number of times. Otherwise, return false.
#
#
#
# Example 1:
#
# Input: start = "_L__R__R_", target = "L______RR"
# Output: true
# Explanation: We can obtain the string target from start by doing the following
# moves:
# - Move the first piece one step to the left, start becomes equal to
# "L___R__R_".
# - Move the last piece one step to the right, start becomes equal to
# "L___R___R".
# - Move the second piece three steps to the right, start becomes equal to
# "L______RR".
# Since it is possible to get the string target from start, we return true.
#
# Example 2:
#
# Input: start = "R_L_", target = "__LR"
# Output: false
# Explanation: The 'R' piece in the string start can move one step to the right
# to obtain "_RL_".
# After that, no pieces can move anymore, so it is impossible to obtain the
# string target from start.
#
# Example 3:
#
# Input: start = "_R", target = "R_"
# Output: false
# Explanation: The piece in the string start can move only to the right, so it
# is impossible to obtain the string target from start.
#
#
#
# Constraints:
#
#
# n == start.length == target.length
#
#
# 1 <= n <= 10^5
#
#
# start and target consist of the characters 'L', 'R', and '_'.
#

# @lc code=start
class Solution:
    def canChange(self, start: str, target: str) -> bool:
        """
        Interview explanation:
        In start, 'L' can move left through '_', 'R' right through '_'; cannot
        cross. Check if start can become target.

        Algorithm:
        - Ignore '_'; L/R sequences must match. For each matched pair, L can
          only move left (start_idx >= target_idx), R only right
          (start_idx <= target_idx).

        Complexity: O(n) time, O(1) space.
        """
        n = len(start)
        i = j = 0
        while True:
            while i < n and start[i] == '_':
                i += 1
            while j < n and target[j] == '_':
                j += 1
            if i == n and j == n:
                return True
            if i == n or j == n or start[i] != target[j]:
                return False
            if start[i] == 'L' and i < j:
                return False
            if start[i] == 'R' and i > j:
                return False
            i += 1
            j += 1

    def canChange_two_pointers(self, start: str, target: str) -> bool:
        """
        Interview explanation:
        Two-pointers over non-blank pieces (same as primary).

        Algorithm:
        - Match piece sequence; enforce L/R movement direction constraints.

        Complexity: O(n) time, O(1) space.
        """
        return self.canChange(start, target)
# @lc code=end
