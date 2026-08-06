#
# @lc app=leetcode id=3996 lang=python3
#
# [3996] Even Number of Knight Moves
#
# https://leetcode.com/problems/even-number-of-knight-moves/description/
#
# algorithms
# Easy (74.84%)
# Likes:    67
# Dislikes: 8
# Total Accepted:    44.5K
# Total Submissions: 59.5K
# Testcase Example:  "[1,1]\n[2,2]"
#
#
# You are given two integer arrays start and target, where each array is
# of the form [x, y] representing a cell on a standard 8 x 8 chessboard.
#
# Return true if a knight can move from start to target in an even number
# of moves. Otherwise, return false.
#
# Note: A valid knight move consists of moving two squares in one
# direction and one square perpendicular to it. The figure below
# illustrates all eight possible moves from a cell.
#
# Example 1:
#
# Input: start = [1,1], target = [2,2]
#
# Output: true
#
# Explanation:
#
# One possible sequence of moves is (1, 1) -> (3, 2) -> (2, 4) -> (4, 3)
# -> (2, 2).
#
# The knight reaches the target in 4 moves, which is even. Thus, the
# answer is true.
#
# Example 2:
#
# Input: start = [4,5], target = [6,6]
#
# Output: false
#
# Explanation:​​​​​​​
#
# It is impossible to reach target = [6, 6] from start = [4, 5] in an even
# number of moves. Thus, the answer is false.
#
# Constraints:
#
# start.length == target.length == 2
#
# 0 <= start[i], target[i] <= 7
#

# @lc code=start
class Solution:
    def canReach(self, start: list[int], target: list[int]) -> bool:
        """
        Interview explanation:
        A knight always changes the parity of x+y (each move changes the sum
        by an odd amount). Even moves preserve color; odd moves flip it.

        Algorithm:
        - Return whether (start[0]+start[1]) and (target[0]+target[1]) have
          the same parity.

        Complexity: O(1) time and space.
        """
        return (start[0] + start[1]) % 2 == (target[0] + target[1]) % 2
# @lc code=end
